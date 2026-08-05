"""A/B runner — the same task, twice, differing only in whether Paritok is on.

Each arm gets a pristine copy of the task repo. Without that, the second arm
would start from the first arm's patch and the comparison would be nonsense.
"""
from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path

import httpx

from .agent import Agent
from .config import PROXY_BASE_URL, RunConfig
from .store import Store

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"
STATS_URL = PROXY_BASE_URL.rsplit("/v1", 1)[0] + "/stats"


def proxy_stats() -> dict | None:
    try:
        r = httpx.get(STATS_URL, timeout=10)
        return r.json() if r.status_code == 200 else None
    except httpx.HTTPError:
        return None


def _stats_delta(before: dict | None, after: dict | None) -> dict | None:
    if not before or not after:
        return None
    keys = ("total_requests", "input_tokens_original", "input_tokens_compressed", "tokens_saved")
    d = {k: after.get(k, 0) - before.get(k, 0) for k in keys}
    orig = d.get("input_tokens_original") or 0
    d["compression_ratio"] = round(d.get("input_tokens_compressed", 0) / orig, 4) if orig else None
    return d


def prepare_workdir(task_dir: Path, pair_id: str, label: str) -> Path:
    dest = RUNS_DIR / pair_id / label
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(task_dir, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return dest


def run_arm(task_dir: Path, pair_id: str, paritok: bool, store: Store,
            strategy: str = "paginate", **cfg_kw) -> dict:
    cfg = RunConfig(paritok=paritok, strategy=strategy, **cfg_kw)
    workdir = prepare_workdir(task_dir, pair_id, cfg.label)
    brief = (task_dir / "TASK.md").read_text()

    before = proxy_stats() if paritok else None
    agent = Agent(cfg, workdir, store)
    result = agent.run(task_dir.name, brief, pair_id=pair_id)
    after = proxy_stats() if paritok else None

    delta = _stats_delta(before, after)
    result["paritok_stats"] = delta
    if delta and result.get("run_id"):
        store.finish_run(result["run_id"], paritok_stats=json.dumps(delta))
    return result


ARM_SPECS = [
    ("truncate", False, "truncate oversized output to fit — survives, but blind"),
    ("paginate", False, "page through everything, uncompressed — nothing lost, full cost"),
    ("paritok", True, "page through everything, compressed — nothing lost, ~1/5 the cost"),
]


def run_pair(task_dir: Path, store: Store, arms: list[str] | None = None, **cfg_kw) -> dict:
    """Run each strategy against a pristine copy of the same task."""
    pair_id = uuid.uuid4().hex[:12]
    specs = [s for s in ARM_SPECS if arms is None or s[0] in arms]
    print(f"\n=== {task_dir.name}  (comparison {pair_id}) ===\n")

    results = {}
    for i, (strategy, paritok, blurb) in enumerate(specs, 1):
        print(f"--- arm {i}/{len(specs)}: {strategy} — {blurb} ---")
        results[strategy] = run_arm(task_dir, pair_id, paritok, store,
                                    strategy=strategy, **cfg_kw)
        print()

    return {"pair_id": pair_id, "task": task_dir.name, "arms": results}


def _verdict(r: dict) -> str:
    if r["outcome"] == "overflow":
        return f"DIED (turn {r['overflow_at_turn']})"
    if r["tests_passed"] is True and r["outcome"] == "solved":
        return "SOLVED"
    if r["outcome"] == "solved":
        return "WRONG FIX"
    return r["outcome"].upper()


def format_comparison(pair: dict) -> str:
    arms = pair["arms"]
    names = list(arms)

    def cell(r, key, fmt="{}"):
        v = r.get(key)
        return "—" if v is None else fmt.format(v)

    rows = [
        ("outcome", [_verdict(arms[n]) for n in names]),
        ("turns", [cell(arms[n], "turns_completed") for n in names]),
        ("peak prompt tokens", [cell(arms[n], "peak_prompt_tokens", "{:,}") for n in names]),
        ("total input tokens", [cell(arms[n], "total_prompt_tokens", "{:,}") for n in names]),
        ("patches applied", [cell(arms[n], "patches_applied") for n in names]),
        ("output truncated", [cell(arms[n], "truncations") + "x" for n in names]),
        ("tests pass", [("yes" if arms[n]["tests_passed"] else "NO") for n in names]),
        ("wall time", [cell(arms[n], "wall_time_s", "{}s") for n in names]),
    ]

    w = max(len(r[0]) for r in rows) + 2
    col = 18
    lines = [
        "\n" + " " * w + "".join(f"{n.upper():<{col}}" for n in names),
        " " * w + "".join(f"{'-' * (col - 2):<{col}}" for _ in names),
    ]
    for label, vals in rows:
        lines.append(f"{label:<{w}}" + "".join(f"{v:<{col}}" for v in vals))

    lines.append("")
    for n in names:
        r = arms[n]
        if r.get("overflow_tokens"):
            lines.append(
                f"  {n}: hit the ceiling at turn {r['overflow_at_turn']} — "
                f"{r['overflow_tokens']:,} tokens against a 32,768 limit."
            )
        if r.get("truncations"):
            lines.append(
                f"  {n}: discarded content from {r['truncations']} tool result(s) "
                f"to stay under budget."
            )
        st = r.get("paritok_stats")
        if st and st.get("input_tokens_original"):
            pct = 100 * st["tokens_saved"] / st["input_tokens_original"]
            lines.append(
                f"  {n}: Paritok compressed {st['input_tokens_original']:,} → "
                f"{st['input_tokens_compressed']:,} tokens across "
                f"{st['total_requests']} requests ({pct:.1f}% saved)."
            )

    # The comparison that matters: same evidence seen, different cost.
    if "paginate" in arms and "paritok" in arms:
        a, b = arms["paginate"]["total_prompt_tokens"], arms["paritok"]["total_prompt_tokens"]
        if a and b:
            lines.append(
                f"\n  Same evidence, same fix: {a:,} → {b:,} input tokens "
                f"({100 * (a - b) / a:.1f}% less) with compression."
            )
    return "\n".join(lines) + "\n"
