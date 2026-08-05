"""The coding agent.

One loop, one model, native tool calls. The *only* thing that differs between
the two arms of a comparison is `RunConfig.base_url` — the agent never learns
whether its context is being compressed. Keeping that knowledge out of here is
what makes the A/B honest.
"""
from __future__ import annotations

import json
import re
import sys
import time
import uuid
from pathlib import Path

import httpx

from .config import RunConfig
from .governor import Governor, TurnRecord, estimate_tokens, is_overflow
from .store import Store
from .tools import SCHEMAS, Toolbox

SYSTEM_PROMPT = """You are a coding agent working in a Python repository.

A test is failing. Your job: find the bug, fix it with apply_patch, and confirm \
the tests pass.

Method:
1. Run the tests first to see the failure.
2. Read the files implicated by the traceback. Read them fully — do not guess.
3. When you are confident, use apply_patch with the exact text to replace.
4. Re-run the tests. If they pass, call finish. If not, keep going.

Rules:
- Change as little as possible. Fix the bug, not the style.
- Never edit the tests to make them pass. That is failure, not success.
- Call exactly one tool per message.
- Large results are paginated. If a result ends with a note saying pages remain,
  call next_page until you have seen everything relevant before concluding.
"""


class Agent:
    def __init__(self, cfg: RunConfig, workdir: Path, store: Store | None = None):
        self.cfg = cfg
        self.tools = Toolbox(
            workdir,
            max_tool_output=cfg.effective_tool_budget,
            paginate=cfg.paginate,
        )
        self.gov = Governor()
        self.store = store
        self.messages: list[dict] = []
        self.client = httpx.Client(timeout=cfg.request_timeout)

    # -- upstream ---------------------------------------------------------
    @staticmethod
    def _is_transient(status: int | None, body: str) -> bool:
        """Shared-capacity noise, not a real failure.

        Featherless returns 'This model is busy' under load, and the plan allows
        only 4 concurrent requests. Retrying these is the difference between a
        run that completes overnight and one that dies on turn 1.
        """
        if status in (429, 500, 502, 503, 504):
            return True
        lowered = body.lower()
        return any(s in lowered for s in ("is busy", "rate limit", "overloaded", "try again"))

    def _post(self) -> tuple[dict | None, str | None, float]:
        """One chat-completions call, with backoff on transient upstream errors."""
        body = {
            "model": self.cfg.model,
            "messages": self.messages,
            "tools": SCHEMAS,
            "tool_choice": "auto",
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.reply_budget,
        }
        t0 = time.time()
        last = "no attempt made"

        for attempt in range(self.cfg.max_retries):
            try:
                r = self.client.post(
                    f"{self.cfg.base_url}/chat/completions",
                    json=body,
                    headers={"Authorization": f"Bearer {self.cfg.api_key}"},
                )
            except httpx.HTTPError as exc:
                last = f"transport: {type(exc).__name__}: {exc}"
                if attempt + 1 < self.cfg.max_retries:
                    time.sleep(self.cfg.retry_backoff * (2 ** attempt))
                    continue
                return None, last, time.time() - t0

            if r.status_code == 200:
                try:
                    return r.json(), None, time.time() - t0
                except ValueError:
                    return None, f"non-JSON response: {r.text[:500]}", time.time() - t0

            last = r.text
            # An overflow is a result, not a retryable fault — return it at once.
            if is_overflow(last) or not self._is_transient(r.status_code, last):
                return None, last, time.time() - t0

            if attempt + 1 < self.cfg.max_retries:
                delay = self.cfg.retry_backoff * (2 ** attempt)
                print(f"  [{self.cfg.label}] upstream busy, retrying in {delay:.0f}s "
                      f"({attempt + 1}/{self.cfg.max_retries - 1})", flush=True)
                time.sleep(delay)

        return None, last, time.time() - t0

    # -- main loop --------------------------------------------------------
    def run(self, task_name: str, task_prompt: str, pair_id: str | None = None) -> dict:
        pair_id = pair_id or uuid.uuid4().hex[:12]
        run_id = (
            self.store.start_run(pair_id, task_name, self.cfg.paritok, self.cfg.model,
                                 self.cfg.strategy)
            if self.store else None
        )

        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task_prompt},
        ]

        started = time.time()
        outcome, error, summary = "max_turns", None, None

        for turn in range(1, self.cfg.max_turns + 1):
            est = estimate_tokens(self.messages, SCHEMAS)
            data, err_body, latency = self._post()

            # Report the *billed* prompt size, not our pre-flight estimate. On
            # the paritok arm those differ by 5x — the estimate is what we hand
            # the proxy, the actual is what survives compression and reaches the
            # model. Showing the estimate made compression look like a no-op.
            actual = ((data or {}).get("usage") or {}).get("prompt_tokens")
            shown = actual or est
            suffix = "" if actual else "  (est)"
            # Only the compressed arm can shrink between what we send and what
            # the model is billed for. The local estimator over-reads by ~30-40%
            # on code and log text, so the threshold has to sit well clear of
            # that bias or turn 1 — where nothing has been compressed yet — gets
            # labelled as a 30% saving.
            if actual and self.cfg.paritok and est > actual * 2.0:
                suffix = f"  ← {est:,} sent, compressed {100 * (1 - actual / est):.0f}%"
            print(f"  [{self.cfg.label}] turn {turn:>2}  {self.gov.bar(shown)}{suffix}",
                  flush=True)

            if err_body is not None:
                rec = TurnRecord(turn, None, est, latency_s=latency, error=err_body[:2000])
                if is_overflow(err_body):
                    self.gov.record_overflow(turn, err_body)
                    rec.actual_prompt_tokens = self.gov.overflow_tokens
                    self.gov.record(rec)
                    if self.store:
                        self.store.add_turn(run_id, rec)
                    tok = self.gov.overflow_tokens
                    print(
                        f"  [{self.cfg.label}] ✗ CONTEXT OVERFLOW at turn {turn}: "
                        f"{tok:,} tokens vs a {self.gov.limit:,} ceiling — the run cannot continue.",
                        flush=True,
                    )
                    outcome, error = "overflow", err_body[:2000]
                else:
                    self.gov.record(rec)
                    if self.store:
                        self.store.add_turn(run_id, rec)
                    print(f"  [{self.cfg.label}] ✗ upstream error: {err_body[:200]}", flush=True)
                    outcome, error = "error", err_body[:2000]
                break

            usage = data.get("usage") or {}
            choice = (data.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            calls = msg.get("tool_calls") or []

            rec = TurnRecord(
                turn=turn,
                tool_name=(calls[0]["function"]["name"] if calls else None),
                estimated_prompt_tokens=est,
                actual_prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                latency_s=latency,
            )

            # Keep the assistant message verbatim so tool_call_ids line up.
            self.messages.append({
                "role": "assistant",
                "content": msg.get("content"),
                **({"tool_calls": calls} if calls else {}),
            })

            if not calls:
                # No tool call: nudge once, then treat as a stall.
                text = (msg.get("content") or "").strip()
                self.gov.record(rec)
                if self.store:
                    self.store.add_turn(run_id, rec)
                if "FINISHED" in text.upper() or turn >= self.cfg.max_turns:
                    outcome, summary = "max_turns", text[:1000]
                    break
                self.messages.append({
                    "role": "user",
                    "content": "Respond with a tool call, not prose. Use run_bash to run the tests.",
                })
                continue

            call = calls[0]
            name = call["function"]["name"]
            try:
                args = json.loads(call["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}

            result = self.tools.call(name, args)
            rec.tool_output_chars = len(result)
            self.gov.record(rec)
            if self.store:
                self.store.add_turn(run_id, rec, args)

            self.messages.append({
                "role": "tool",
                "tool_call_id": call.get("id", f"call_{turn}"),
                "content": result,
            })

            # Drop any sibling calls the model emitted; we answer one per turn.
            for extra in calls[1:]:
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": extra.get("id", f"call_{turn}_x"),
                    "content": "SKIPPED: issue one tool call per message.",
                })

            if name == "finish":
                outcome, summary = "solved", args.get("summary", "")
                print(f"  [{self.cfg.label}] ✓ finished at turn {turn}", flush=True)
                break

        wall = time.time() - started
        tests_passed = self._verify()

        if outcome == "solved" and not tests_passed:
            outcome = "claimed_solved_but_tests_fail"

        result = {
            "run_id": run_id,
            "pair_id": pair_id,
            "label": self.cfg.label,
            "outcome": outcome,
            "turns_completed": len(self.gov.turns),
            "total_prompt_tokens": self.gov.total_prompt_tokens,
            "peak_prompt_tokens": self.gov.peak_prompt_tokens,
            "overflow_at_turn": self.gov.overflowed_at_turn,
            "overflow_tokens": self.gov.overflow_tokens,
            "tests_passed": tests_passed,
            "patches_applied": self.tools.patches_applied,
            "truncations": self.tools.truncations,
            "strategy": self.cfg.strategy,
            "wall_time_s": round(wall, 1),
            "summary": summary,
            "error": error,
        }

        if self.store:
            self.store.save_transcript(run_id, self.messages)
            self.store.finish_run(
                run_id,
                outcome=outcome,
                turns_completed=result["turns_completed"],
                total_prompt_tokens=result["total_prompt_tokens"],
                peak_prompt_tokens=result["peak_prompt_tokens"],
                overflow_at_turn=result["overflow_at_turn"],
                overflow_tokens=result["overflow_tokens"],
                tests_passed=None if tests_passed is None else int(tests_passed),
                patches_applied=result["patches_applied"],
                truncations=result["truncations"],
                wall_time_s=result["wall_time_s"],
                error=error,
            )
        return result

    def _verify(self) -> bool | None:
        """Ground truth: run the task's tests ourselves, ignoring what the model claims.

        Deliberately unpiped. An earlier version ran `pytest | tail -5`, which
        reports *tail's* exit status — so every run looked green regardless of
        whether the tests passed.
        """
        out = self.tools.call("run_bash", {"cmd": f"{sys.executable} -m pytest -q"})
        m = re.search(r"\(exit (\d+)\)", out)
        return None if not m else m.group(1) == "0"
