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


def run_arm(task_dir: Path, pair_id: str, paritok: bool, store: Store, **cfg_kw) -> dict:
    cfg = RunConfig(paritok=paritok, **cfg_kw)
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


def run_pair(task_dir: Path, store: Store, **cfg_kw) -> dict:
    pair_id = uuid.uuid4().hex[:12]
    print(f"\n=== {task_dir.name}  (pair {pair_id}) ===\n")

    print("--- arm 1/2: Paritok OFF (direct to Featherless) ---")
    off = run_arm(task_dir, pair_id, False, store, **cfg_kw)

    print("\n--- arm 2/2: Paritok ON (through the compression proxy) ---")
    on = run_arm(task_dir, pair_id, True, store, **cfg_kw)

    return {"pair_id": pair_id, "task": task_dir.name, "off": off, "on": on}


def format_comparison(pair: dict) -> str:
    off, on = pair["off"], pair["on"]

    def cell(r, key, fmt="{}"):
        v = r.get(key)
        return "—" if v is None else fmt.format(v)

    rows = [
        ("outcome", off["outcome"], on["outcome"]),
        ("turns completed", cell(off, "turns_completed"), cell(on, "turns_completed")),
        ("peak prompt tokens", cell(off, "peak_prompt_tokens", "{:,}"), cell(on, "peak_prompt_tokens", "{:,}")),
        ("total prompt tokens", cell(off, "total_prompt_tokens", "{:,}"), cell(on, "total_prompt_tokens", "{:,}")),
        ("patches applied", cell(off, "patches_applied"), cell(on, "patches_applied")),
        ("tests pass", str(off["tests_passed"]), str(on["tests_passed"])),
        ("wall time", cell(off, "wall_time_s", "{}s"), cell(on, "wall_time_s", "{}s")),
    ]

    w = max(len(r[0]) for r in rows) + 2
    lines = [
        f"\n{'':<{w}}{'PARITOK OFF':<22}{'PARITOK ON':<22}",
        f"{'':<{w}}{'-' * 20:<22}{'-' * 20:<22}",
    ]
    for label, a, b in rows:
        lines.append(f"{label:<{w}}{a:<22}{b:<22}")

    if off.get("overflow_tokens"):
        lines.append(
            f"\n  Paritok OFF hit the ceiling at turn {off['overflow_at_turn']}: "
            f"{off['overflow_tokens']:,} tokens against a 32,768 limit."
        )
    st = on.get("paritok_stats")
    if st and st.get("input_tokens_original"):
        saved = st["tokens_saved"]
        pct = 100 * saved / st["input_tokens_original"]
        lines.append(
            f"  Paritok compressed {st['input_tokens_original']:,} → "
            f"{st['input_tokens_compressed']:,} tokens across {st['total_requests']} requests "
            f"({pct:.1f}% saved)."
        )
    return "\n".join(lines) + "\n"
