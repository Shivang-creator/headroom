"""Context accounting — how close the conversation is to the upstream ceiling.

Two sources of truth, in order of preference:

1. `usage.prompt_tokens` from a successful response — exact, but only available
   after the call succeeds.
2. The rejection message itself. Featherless states the exact size of the
   prompt it refused ("Your prompt has 35627 tokens"), so an overflow is a
   *measurement*, not just a failure. That is what makes the paritok-off arm
   quantifiable instead of a dead end.

The local estimate is only used to draw the headroom bar before a call returns.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .config import UPSTREAM_CONTEXT_LIMIT

# Featherless: "Maximum context length for model 'X' allowed on your plan is
# 32768 tokens. Your prompt has 35627 tokens, which exceeds the maximum ..."
_OVERFLOW_RE = re.compile(r"prompt has (\d+) tokens", re.I)
_LIMIT_RE = re.compile(r"is (\d+) tokens", re.I)

# Calibrated against observed prompt_tokens on this workload: a 103,371-byte
# payload measured 35,627 tokens => ~2.90 bytes/token. Code and log text are
# denser than prose, so the usual /4 rule understates by ~25%.
_BYTES_PER_TOKEN = 2.9


def estimate_tokens(messages: list[dict], tools: list[dict] | None = None) -> int:
    """Cheap local estimate, used only for the live headroom display."""
    payload = json.dumps(messages, ensure_ascii=False)
    n = len(payload) / _BYTES_PER_TOKEN
    if tools:
        n += len(json.dumps(tools, ensure_ascii=False)) / _BYTES_PER_TOKEN
    return int(n)


def parse_overflow(error_body: str) -> tuple[int | None, int | None]:
    """Pull (prompt_tokens, limit) out of a context_length_exceeded body."""
    prompt = _OVERFLOW_RE.search(error_body)
    limit = _LIMIT_RE.search(error_body)
    return (
        int(prompt.group(1)) if prompt else None,
        int(limit.group(1)) if limit else None,
    )


def is_overflow(error_body: str) -> bool:
    return "context_length_exceeded" in error_body or "maximum context length" in error_body.lower()


@dataclass
class TurnRecord:
    turn: int
    tool_name: str | None
    estimated_prompt_tokens: int
    actual_prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_s: float = 0.0
    tool_output_chars: int = 0
    error: str | None = None

    @property
    def prompt_tokens(self) -> int:
        return self.actual_prompt_tokens or self.estimated_prompt_tokens

    @property
    def headroom_pct(self) -> float:
        """How much of the plan's ceiling is still free, 0-100."""
        used = min(self.prompt_tokens, UPSTREAM_CONTEXT_LIMIT)
        return round(100.0 * (1 - used / UPSTREAM_CONTEXT_LIMIT), 1)


@dataclass
class Governor:
    """Tracks context growth across a run and reports when it hits the wall."""

    limit: int = UPSTREAM_CONTEXT_LIMIT
    turns: list[TurnRecord] = field(default_factory=list)
    overflowed_at_turn: int | None = None
    overflow_tokens: int | None = None

    def record(self, rec: TurnRecord) -> None:
        self.turns.append(rec)

    def record_overflow(self, turn: int, error_body: str) -> None:
        tokens, limit = parse_overflow(error_body)
        self.overflowed_at_turn = turn
        self.overflow_tokens = tokens
        if limit:
            self.limit = limit

    @property
    def total_prompt_tokens(self) -> int:
        return sum(t.prompt_tokens for t in self.turns)

    @property
    def peak_prompt_tokens(self) -> int:
        return max((t.prompt_tokens for t in self.turns), default=0)

    def bar(self, tokens: int, width: int = 28) -> str:
        """A headroom bar for the terminal. Overflow renders past the wall."""
        frac = tokens / self.limit
        filled = min(int(frac * width), width)
        s = "█" * filled + "░" * (width - filled)
        return f"{s} {tokens:>6,}/{self.limit:,}" + ("  OVER" if frac > 1 else "")
