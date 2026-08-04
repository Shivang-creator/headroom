"""Find the largest single block the hosted compressor can actually handle.

Motivation: a 37,620-token block of repetitive pytest output — close to the
best-case input for a compressor — came back `skipped: below_refusal_threshold`.
Highly repetitive text failing to compress points at a size limit rather than a
content problem, and `compression.max_tokens` defaults to 50,000, which is above
wherever that limit actually is.

    python tools/probe_block_size.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from headroom.config import _load_keys  # noqa: E402

COMPRESS_URL = "https://www.paritok.com/api/compress"
BYTES_PER_TOKEN = 2.9

# Realistic pytest failure output — repetitive, which is the easy case.
UNIT = (
    "FAILED tests/test_grid.py::test_every_cell_is_weighted_correctly[{i}-{j}] - "
    "AssertionError: assert 14 == 42\n"
    "E         + where 14 = evaluate(18, 18)[{i}][{j}]\n"
    "E         and   42 = expected({i}, {j})\n"
)


def block_of(target_tokens: int) -> str:
    target_chars = int(target_tokens * BYTES_PER_TOKEN)
    out, i = [], 0
    size = 0
    while size < target_chars:
        s = UNIT.format(i=i % 18, j=(i // 18) % 18)
        out.append(s)
        size += len(s)
        i += 1
    return "".join(out)


def probe(client: httpx.Client, key: str, target: int) -> dict:
    content = block_of(target)
    actual = int(len(content) / BYTES_PER_TOKEN)
    t0 = time.time()
    try:
        r = client.post(
            COMPRESS_URL,
            json={"content": content, "model": "paritok-4b-v1"},
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
    except httpx.HTTPError as exc:
        return {"target": target, "actual": actual, "error": f"{type(exc).__name__}"}
    dt = time.time() - t0
    if r.status_code != 200:
        return {"target": target, "actual": actual, "http": r.status_code, "elapsed": round(dt, 1)}
    comp = r.json().get("compressed", "")
    out_tokens = int(len(comp) / BYTES_PER_TOKEN)
    return {
        "target": target,
        "actual": actual,
        "out_tokens": out_tokens,
        "ratio": round(out_tokens / actual, 4) if actual else None,
        "empty": not comp.strip(),
        "elapsed": round(dt, 1),
    }


def main() -> None:
    key = _load_keys()["PARITOK_API_KEY"]
    sizes = [1_000, 2_000, 4_000, 6_000, 8_000, 12_000, 16_000, 24_000, 32_000, 40_000]
    results = []
    print(f"{'in tokens':>10} {'out':>8} {'ratio':>8} {'empty':>6} {'secs':>6}")
    print("-" * 44)
    with httpx.Client(timeout=300) as client:
        for s in sizes:
            res = probe(client, key, s)
            results.append(res)
            if "error" in res or "http" in res:
                print(f"{res['actual']:>10,} {'—':>8} {'—':>8} {'—':>6} "
                      f"{res.get('elapsed', '—'):>6}  {res.get('error') or 'HTTP ' + str(res.get('http'))}")
                continue
            print(f"{res['actual']:>10,} {res['out_tokens']:>8,} {res['ratio']:>8} "
                  f"{str(res['empty']):>6} {res['elapsed']:>6}", flush=True)

    good = [r for r in results if r.get("ratio") is not None and not r.get("empty")
            and r["ratio"] < 0.95]
    if good:
        print(f"\nlargest block that compressed usefully: {max(r['actual'] for r in good):,} tokens")
    bad = [r for r in results if r.get("empty") or (r.get("ratio") or 0) >= 0.95]
    if bad:
        print(f"smallest block that failed to compress:  {min(r['actual'] for r in bad):,} tokens")

    Path(__file__).parent.joinpath("block_size_results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
