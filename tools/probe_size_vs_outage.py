"""Is the passthrough size-dependent, or a transient GPU outage?

Two hypotheses for `/api/compress` returning its input unchanged:

  H1 (size)    blocks above ~6,000 tokens are refused by a size guard.
  H2 (outage)  the hosted GPU drops out for periods and echoes everything back,
               per issue #30. Raised on issue #31 by @shlok-temp, +1 @mdnuhuslom30.

These make opposite predictions, and one experiment separates them: alternate a
small block and a large block back to back, many times.

  If H1: within every adjacent pair, the small one compresses and the large one
         does not — regardless of when the pair runs.
  If H2: failures cluster in TIME. Both members of a pair fail together during an
         outage window and both succeed outside it.

The `gpu_available` flag in each response is recorded too. Issue #30 reports that
/api/compress sets it false while the GPU is down, so if large blocks come back
verbatim with gpu_available:true, that also separates the two.

    python tools/probe_size_vs_outage.py [pairs]
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
SMALL_TOKENS = 3_000     # inside the band that worked
LARGE_TOKENS = 8_000     # above the suspected cliff

UNIT = ("FAILED tests/test_grid.py::test_every_cell_is_weighted_correctly[{i}-{j}] - "
        "AssertionError: assert 14 == 42\n"
        "E         + where 14 = evaluate(18, 18)[{i}][{j}]\n")


def block_of(target_tokens: int) -> str:
    target = int(target_tokens * BYTES_PER_TOKEN)
    out, size, i = [], 0, 0
    while size < target:
        s = UNIT.format(i=i % 18, j=(i // 18) % 18)
        out.append(s); size += len(s); i += 1
    return "".join(out)


def probe(client: httpx.Client, key: str, content: str, label: str, t_start: float) -> dict:
    t0 = time.time()
    try:
        r = client.post(COMPRESS_URL,
                        json={"content": content, "model": "paritok-4b-v1"},
                        headers={"Authorization": f"Bearer {key}"})
        body = r.json()
    except (httpx.HTTPError, ValueError) as exc:
        return {"label": label, "error": type(exc).__name__, "t": round(time.time() - t_start, 1)}
    out = body.get("compressed", "")
    ratio = len(out) / len(content) if content else 1.0
    return {
        "label": label,
        "in_tokens": int(len(content) / BYTES_PER_TOKEN),
        "out_tokens": int(len(out) / BYTES_PER_TOKEN),
        "ratio": round(ratio, 4),
        "compressed": ratio < 0.95 and bool(out.strip()),
        "empty": not out.strip(),
        "gpu_available": body.get("gpu_available"),
        "elapsed": round(time.time() - t0, 1),
        "t": round(time.time() - t_start, 1),
    }


def main() -> None:
    pairs = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    key = _load_keys()["PARITOK_API_KEY"]
    small, large = block_of(SMALL_TOKENS), block_of(LARGE_TOKENS)
    rows, t_start = [], time.time()

    print(f"{len(small)/BYTES_PER_TOKEN:.0f}-token vs {len(large)/BYTES_PER_TOKEN:.0f}-token "
          f"blocks, alternating, {pairs} pairs\n")
    print(f"{'t+s':>6} {'size':>6} {'ratio':>7} {'gpu_ok':>7} {'secs':>5}  verdict")
    print("-" * 52)

    with httpx.Client(timeout=300) as client:
        for _ in range(pairs):
            for label, content in (("SMALL", small), ("LARGE", large)):
                r = probe(client, key, content, label, t_start)
                rows.append(r)
                if "error" in r:
                    print(f"{r['t']:>6} {label:>6} {'—':>7} {'—':>7} {'—':>5}  ERROR {r['error']}")
                    continue
                verdict = "compressed" if r["compressed"] else ("EMPTY" if r["empty"] else "VERBATIM")
                print(f"{r['t']:>6} {label:>6} {r['ratio']:>7} {str(r['gpu_available']):>7} "
                      f"{r['elapsed']:>5}  {verdict}", flush=True)

    ok = [r for r in rows if "error" not in r]
    s_ok = [r for r in ok if r["label"] == "SMALL"]
    l_ok = [r for r in ok if r["label"] == "LARGE"]
    s_comp = sum(r["compressed"] for r in s_ok)
    l_comp = sum(r["compressed"] for r in l_ok)

    print("\n" + "=" * 52)
    print(f"SMALL ({SMALL_TOKENS} tok): compressed {s_comp}/{len(s_ok)}")
    print(f"LARGE ({LARGE_TOKENS} tok): compressed {l_comp}/{len(l_ok)}")
    print(f"gpu_available true on every response: "
          f"{all(r['gpu_available'] is True for r in ok)}")

    # Pairs where the two members disagree are only possible under H1.
    split = sum(1 for i in range(0, len(ok) - 1, 2)
                if ok[i]["compressed"] != ok[i + 1]["compressed"])
    print(f"adjacent pairs that DISAGREE (small ok, large not): {split}/{len(ok)//2}")

    print()
    if s_comp == len(s_ok) and l_comp == 0:
        print("=> SIZE-DEPENDENT (H1). Small always compresses, large never does,")
        print("   interleaved in the same time windows. Not a transient outage.")
    elif s_comp == 0 and l_comp == 0:
        print("=> Everything failed. Consistent with an OUTAGE (H2) right now —")
        print("   rerun later, this run cannot separate the hypotheses.")
    elif split == 0:
        print("=> Failures track TIME, not size (H2). The commenters are right.")
    else:
        print("=> Mixed. See the per-request timings above.")

    Path(__file__).parent.joinpath("size_vs_outage_results.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
