"""Runtime configuration for Headroom.

Everything that differs between the two arms of an A/B run lives here, so the
agent itself has no idea whether compression is on. That matters: if the agent
could branch on it, the comparison would be worthless.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The Featherless plan ceiling. Not the model's native context (202,752 for
# GLM-4.7-Flash) — the cap the *plan* enforces, which is what actually rejects
# requests. Verified empirically: a 35,627-token prompt returns HTTP 400.
UPSTREAM_CONTEXT_LIMIT = 32_768

DIRECT_BASE_URL = "https://api.featherless.ai/v1"
PROXY_BASE_URL = "http://127.0.0.1:8080/v1"

# Chosen by tools/probe_models.py, not by reading the catalogue. GLM-4.7-Flash
# looked like the obvious pick (cheapest concurrency cost) but measured 50.3s
# p50 with a 1-in-3 failure rate; GLM-5.1 measured 2.7s with 3/3 tool calls.
# Native context 202,752 — the plan still caps it at 32,768, which is the point.
DEFAULT_MODEL = "zai-org/GLM-5.1"

# What a truncating agent keeps: ~24,000 chars ≈ 8,300 tokens. Roughly a quarter
# of the ceiling, which is a realistic budget to give one tool result when you
# still need room for the rest of the conversation.
TRUNCATE_BUDGET = 24_000


@lru_cache(maxsize=1)
def _load_keys() -> dict[str, str]:
    """Read keys from the env, falling back to the brainstorm folder's .keys.env.

    The fallback exists so the overnight build works unattended; anyone else
    running this just exports the two variables.
    """
    keys = {
        "FEATHERLESS_API_KEY": os.environ.get("FEATHERLESS_API_KEY", ""),
        "PARITOK_API_KEY": os.environ.get("PARITOK_API_KEY", ""),
    }
    if all(keys.values()):
        return keys

    candidates = [
        Path(os.environ.get("HEADROOM_KEYS_FILE", "")),
        REPO_ROOT / ".keys.env",
        Path.home() / "Projects/Hackathon Brainstorming/Ideas/Build with Paritok/.keys.env",
    ]
    for path in candidates:
        if not path or not path.is_file():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip()
            if k in keys and not keys[k]:
                keys[k] = v
        if all(keys.values()):
            break
    return keys


# The three strategies anyone actually has for oversized tool output.
#
#   truncate  cut it to fit and hope the informative part survived. What most
#             agents do today, and it is not a straw man — it is cheap and it
#             usually works. It also silently discards evidence.
#   paginate  page through the whole thing, uncompressed. Nothing is lost, but
#             every page costs full-price context against the ceiling.
#   paritok   page through it *and* compress each page. Nothing lost, ~1/5 the
#             context.
#
# Comparing only "compression on/off" hides the fact that the honest baseline
# is truncation, so all three run.
ARMS = ("truncate", "paginate", "paritok")


@dataclass(frozen=True)
class RunConfig:
    """One arm of a comparison."""

    paritok: bool
    # How this arm handles a tool result bigger than its budget.
    strategy: str = "paginate"
    model: str = DEFAULT_MODEL
    max_turns: int = 40
    temperature: float = 0.0
    # Leave room for the model's own reply inside the plan's ceiling.
    reply_budget: int = 1_024
    request_timeout: float = 300.0
    # Featherless allows 4 concurrent requests and returns "This model is busy"
    # under load; without backoff an overnight run dies on the first turn.
    max_retries: int = 6
    retry_backoff: float = 4.0
    # Characters of tool output the agent carries. See tools.DEFAULT_MAX_TOOL_OUTPUT
    # — this is the parameter the whole comparison turns on.
    max_tool_output: int = 120_000

    @property
    def base_url(self) -> str:
        return PROXY_BASE_URL if self.paritok else DIRECT_BASE_URL

    @property
    def label(self) -> str:
        return {"truncate": "truncate", "paginate": "paginate", "paritok": "paritok"}[self.strategy]

    @property
    def paginate(self) -> bool:
        return self.strategy in ("paginate", "paritok")

    @property
    def effective_tool_budget(self) -> int:
        """Truncating agents run a much smaller budget — that is the point of
        the strategy. Paginating arms carry the full result across pages."""
        return TRUNCATE_BUDGET if self.strategy == "truncate" else self.max_tool_output

    @property
    def api_key(self) -> str:
        # Both arms authenticate to Featherless; the proxy forwards the header
        # upstream untouched and adds its own auth to the compression service.
        return _load_keys()["FEATHERLESS_API_KEY"]
