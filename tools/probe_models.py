"""Pick a model that can actually carry an overnight agent run.

Three things have to be true, and the model list on featherless.ai tells you
none of them: the model must be reachable right now, it must emit native tool
calls (Paritok only compresses `role:"tool"` blocks, so a model that ignores
tools defeats the whole design), and it must answer fast enough that 30 turns
finish this side of the deadline.

    python tools/probe_models.py
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from headroom.config import DIRECT_BASE_URL, _load_keys  # noqa: E402

CANDIDATES = [
    "zai-org/GLM-4.7-Flash",
    "zai-org/GLM-4.7",
    "zai-org/GLM-5.1",
    "deepseek-ai/DeepSeek-V3.2",
    "deepseek-ai/DeepSeek-V3.1-Terminus",
    "moonshotai/Kimi-K2.7-Code",
    "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
]

TOOLS = [{
    "type": "function",
    "function": {
        "name": "run_bash",
        "description": "Run a shell command in the repo.",
        "parameters": {
            "type": "object",
            "properties": {"cmd": {"type": "string"}},
            "required": ["cmd"],
        },
    },
}]

PROMPT = [
    {"role": "system", "content": "You are a coding agent. Always respond with a tool call."},
    {"role": "user", "content": "Run the test suite in this repo to see what is failing."},
]

TRIALS = 3


def probe(client: httpx.Client, key: str, model: str) -> dict:
    latencies, tool_calls, errors = [], 0, []
    for _ in range(TRIALS):
        t0 = time.time()
        try:
            r = client.post(
                f"{DIRECT_BASE_URL}/chat/completions",
                json={"model": model, "messages": PROMPT, "tools": TOOLS,
                      "tool_choice": "auto", "max_tokens": 128, "temperature": 0},
                headers={"Authorization": f"Bearer {key}"},
            )
        except httpx.HTTPError as exc:
            errors.append(f"{type(exc).__name__}")
            continue
        dt = time.time() - t0
        if r.status_code != 200:
            try:
                errors.append(r.json()["error"]["message"][:60])
            except Exception:
                errors.append(f"HTTP {r.status_code}")
            continue
        latencies.append(dt)
        msg = (r.json().get("choices") or [{}])[0].get("message") or {}
        if msg.get("tool_calls"):
            tool_calls += 1

    return {
        "model": model,
        "ok": len(latencies),
        "tool_calls": tool_calls,
        "p50_s": round(statistics.median(latencies), 1) if latencies else None,
        "errors": errors[:2],
    }


def main() -> None:
    key = _load_keys()["FEATHERLESS_API_KEY"]
    results = []
    with httpx.Client(timeout=120) as client:
        for model in CANDIDATES:
            res = probe(client, key, model)
            flag = "OK " if res["ok"] == TRIALS and res["tool_calls"] == TRIALS else "   "
            print(f"{flag}{model:<40} ok={res['ok']}/{TRIALS} tools={res['tool_calls']}/{TRIALS} "
                  f"p50={res['p50_s']}s {res['errors'] or ''}", flush=True)
            results.append(res)

    usable = [r for r in results if r["ok"] == TRIALS and r["tool_calls"] == TRIALS]
    usable.sort(key=lambda r: r["p50_s"])
    print("\nranked (reliable + tool-calling, fastest first):")
    for r in usable:
        print(f"  {r['p50_s']:>5}s  {r['model']}")
    if usable:
        print(f"\nrecommended DEFAULT_MODEL = {usable[0]['model']!r}")
    else:
        print("\nnothing passed all three checks — rerun, capacity fluctuates")

    Path(__file__).parent.joinpath("probe_results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
