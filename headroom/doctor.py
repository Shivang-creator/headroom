"""Preflight checks.

Every check here corresponds to something that actually went wrong while
building this, and that produced no useful error at the time:

- compression silently not firing because the message format was wrong
- compression silently not firing because context_window was 200000
- max_tokens configured above the size where the compressor stops working
- a model that looks fine in the catalogue and times out in practice

Paritok's own issue #29 asks for a preflight doctor command. This is ours.

    python -m headroom doctor
"""
from __future__ import annotations


import httpx

from .config import (
    DIRECT_BASE_URL, PROXY_BASE_URL, REPO_ROOT, UPSTREAM_CONTEXT_LIMIT,
    DEFAULT_MODEL, _load_keys,
)

OK, WARN, FAIL = "✓", "!", "✗"
COMPRESSOR_SAFE_BLOCK = 4_000   # measured: compresses reliably


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, status: str, name: str, detail: str = "") -> None:
        self.rows.append((status, name, detail))
        colour = {OK: "\033[32m", WARN: "\033[33m", FAIL: "\033[31m"}.get(status, "")
        print(f"  {colour}{status}\033[0m {name}" + (f" — {detail}" if detail else ""), flush=True)

    @property
    def failures(self) -> int:
        return sum(1 for s, _, _ in self.rows if s == FAIL)

    @property
    def warnings(self) -> int:
        return sum(1 for s, _, _ in self.rows if s == WARN)


def _yaml_value(text: str, key: str) -> str | None:
    """Deliberately dependency-free — this must run before anything is set up."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            val = stripped.split(":", 1)[1].strip()
            return val.split("#")[0].strip() or None
    return None


def check_keys(r: Report) -> dict:
    keys = _load_keys()
    for name in ("PARITOK_API_KEY", "FEATHERLESS_API_KEY"):
        if keys.get(name):
            r.add(OK, name, f"set ({keys[name][:7]}…)")
        else:
            r.add(FAIL, name, "missing — export it or put it in .keys.env")
    return keys


def check_config(r: Report) -> None:
    path = REPO_ROOT / "paritok.yaml"
    if not path.is_file():
        r.add(FAIL, "paritok.yaml", "not found — run `paritok init`")
        return
    text = path.read_text()

    if _yaml_value(text, "use_gpu_server") == "true":
        r.add(OK, "use_gpu_server", "true (hosted GPU)")
    else:
        r.add(WARN, "use_gpu_server", "not true — the hackathon requires the hosted GPU")

    window = _yaml_value(text, "context_window")
    if window and window.isdigit():
        w = int(window)
        if w > UPSTREAM_CONTEXT_LIMIT * 2:
            r.add(FAIL, "history.context_window", (
                f"{w:,} but the upstream ceiling is {UPSTREAM_CONTEXT_LIMIT:,}. "
                f"Compression triggers at 80% of this ({int(w * 0.8):,} tokens), which the "
                f"upstream will never accept — so it never fires. Set it to "
                f"{UPSTREAM_CONTEXT_LIMIT}."))
        else:
            r.add(OK, "history.context_window", f"{w:,} (matches the upstream ceiling)")

    # An earlier version warned that max_tokens above ~6,000 was unsafe. That was
    # based on a block-size limit we measured but that turned out to be a transient
    # backend outage — retracted, see docs/FINDINGS.md §4. No warning is warranted.


def check_gpu(r: Report, keys: dict) -> None:
    if not keys.get("PARITOK_API_KEY"):
        return
    try:
        resp = httpx.get("https://www.paritok.com/api/test",
                         headers={"Authorization": f"Bearer {keys['PARITOK_API_KEY']}"},
                         timeout=30)
    except httpx.HTTPError as exc:
        r.add(FAIL, "Paritok hosted GPU", f"unreachable: {type(exc).__name__}")
        return
    if resp.status_code != 200:
        r.add(FAIL, "Paritok hosted GPU", f"HTTP {resp.status_code}")
        return
    body = resp.json()
    if body.get("gpu_available"):
        r.add(OK, "Paritok hosted GPU", body.get("message", "online"))
    else:
        r.add(FAIL, "Paritok hosted GPU", f"gpu_available=false: {body}")


def check_compression_actually_fires(r: Report, keys: dict) -> None:
    """The check that would have saved three hours.

    A block inside the working band must come back materially smaller. If it
    doesn't, compression is a no-op and every downstream number is meaningless.
    """
    if not keys.get("PARITOK_API_KEY"):
        return
    unit = ("FAILED tests/test_grid.py::test_cell[{i}] - AssertionError: "
            "assert 14 == 42\nE   + where 14 = evaluate(18, 18)\n")
    content = "".join(unit.format(i=i) for i in range(int(COMPRESSOR_SAFE_BLOCK * 2.9 / 100)))
    try:
        resp = httpx.post("https://www.paritok.com/api/compress",
                          json={"content": content, "model": "paritok-4b-v1"},
                          headers={"Authorization": f"Bearer {keys['PARITOK_API_KEY']}"},
                          timeout=120)
        out = resp.json().get("compressed", "")
    except (httpx.HTTPError, ValueError) as exc:
        r.add(FAIL, "compression smoke test", f"{type(exc).__name__}")
        return

    ratio = len(out) / len(content) if content else 1.0
    if not out.strip():
        r.add(WARN, "compression smoke test", "returned empty — query-conditioned, or a GPU fault")
    elif ratio > 0.95:
        r.add(FAIL, "compression smoke test", (
            f"input returned ~verbatim (ratio {ratio:.2f}). Compression is a no-op; "
            f"any savings you measure will be zero."))
    else:
        r.add(OK, "compression smoke test",
              f"{len(content):,} → {len(out):,} chars (ratio {ratio:.3f})")


def check_proxy(r: Report) -> bool:
    url = PROXY_BASE_URL.rsplit("/v1", 1)[0] + "/stats"
    try:
        resp = httpx.get(url, timeout=10)
    except httpx.HTTPError:
        r.add(FAIL, "Paritok proxy", "not answering on :8080 — see RUNME.md step 1")
        return False
    if resp.status_code != 200:
        r.add(FAIL, "Paritok proxy", f"HTTP {resp.status_code}")
        return False
    r.add(OK, "Paritok proxy", f"up — {resp.json().get('total_requests', 0)} requests so far")
    return True


def check_upstream(r: Report, keys: dict) -> None:
    if not keys.get("FEATHERLESS_API_KEY"):
        return
    tools = [{"type": "function", "function": {
        "name": "run_bash", "description": "run a shell command",
        "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}}}}]
    try:
        resp = httpx.post(f"{DIRECT_BASE_URL}/chat/completions",
                          json={"model": DEFAULT_MODEL, "max_tokens": 64, "temperature": 0,
                                "tools": tools, "tool_choice": "auto",
                                "messages": [{"role": "user", "content": "Run the test suite."}]},
                          headers={"Authorization": f"Bearer {keys['FEATHERLESS_API_KEY']}"},
                          timeout=120)
    except httpx.HTTPError as exc:
        r.add(FAIL, f"upstream {DEFAULT_MODEL}", f"{type(exc).__name__}")
        return
    if resp.status_code != 200:
        detail = resp.text[:120]
        r.add(FAIL, f"upstream {DEFAULT_MODEL}", detail)
        return
    msg = (resp.json().get("choices") or [{}])[0].get("message") or {}
    if msg.get("tool_calls"):
        r.add(OK, f"upstream {DEFAULT_MODEL}", "reachable, emits native tool calls")
    else:
        r.add(FAIL, f"upstream {DEFAULT_MODEL}", (
            "reachable but did NOT emit a native tool call. Paritok only compresses "
            "role:\"tool\" blocks, so compression would be a no-op with this model."))


def main() -> int:
    print("\nHeadroom preflight\n" + "─" * 60)
    r = Report()

    print("\nCredentials")
    keys = check_keys(r)

    print("\nConfiguration")
    check_config(r)

    print("\nParitok")
    check_gpu(r, keys)
    check_compression_actually_fires(r, keys)
    check_proxy(r)

    print("\nUpstream")
    check_upstream(r, keys)

    print("─" * 60)
    if r.failures:
        print(f"\n{r.failures} check(s) failed, {r.warnings} warning(s). "
              f"Fix the failures before trusting any numbers.\n")
        return 1
    if r.warnings:
        print(f"\nAll critical checks passed, {r.warnings} warning(s).\n")
        return 0
    print("\nAll checks passed. `python -m headroom ab tasks/task01_report_mean` is safe to run.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
