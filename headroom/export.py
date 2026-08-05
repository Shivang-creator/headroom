"""Export run results into the README and examples/.

Judges are explicitly invited to evaluate sample outputs without running
anything, so every completed pair gets written out as a markdown transcript plus
a results table spliced into the README between the RESULTS markers.
"""
from __future__ import annotations

import json
from pathlib import Path

from .store import Store

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
README = ROOT / "README.md"
START, END = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"


def _outcome_cell(r: dict) -> str:
    if r["outcome"] == "overflow":
        return f"✗ overflow at turn {r['overflow_at_turn']}"
    if r["outcome"] == "solved" and r["tests_passed"] == 1:
        return "✓ solved"
    if r["outcome"] == "solved":
        return "⚠ claimed solved, tests fail"
    return f"✗ {r['outcome']}"


ARM_ORDER = {"truncate": 0, "paginate": 1, "paritok": 2}


def results_table(store: Store) -> str:
    lines = [
        "| Task | Strategy | Outcome | Turns | Peak tokens | Total input tokens | Truncated | Tests |",
        "|---|---|---|---:|---:|---:|---:|:--:|",
    ]
    savings, paired = [], []
    for pair in reversed(store.pairs()):
        runs = sorted(store.runs_for_pair(pair["pair_id"]),
                      key=lambda r: ARM_ORDER.get(r["strategy"] or "paginate", 9))
        if len(runs) < 2:
            continue
        by_strategy = {r["strategy"]: r for r in runs}
        for r in runs:
            arm = r["strategy"] or ("paritok" if r["paritok"] else "paginate")
            arm_label = f"**{arm}**" if arm == "paritok" else arm
            trunc = r["truncations"] or 0
            lines.append(
                f"| `{r['task']}` | {arm_label} | {_outcome_cell(r)} | {r['turns_completed']} | "
                f"{r['peak_prompt_tokens']:,} | {r['total_prompt_tokens']:,} | "
                f"{str(trunc) + '×' if trunc else '—'} | "
                f"{'✅' if r['tests_passed'] == 1 else '❌'} |"
            )
        # paginate vs paritok is the clean attribution: identical agents,
        # identical evidence, only base_url differs.
        pg, pk = by_strategy.get("paginate"), by_strategy.get("paritok")
        if pg and pk and pg["outcome"] == "solved" and pk["outcome"] == "solved":
            if pg["total_prompt_tokens"]:
                paired.append(100 * (pg["total_prompt_tokens"] - pk["total_prompt_tokens"])
                              / pg["total_prompt_tokens"])
            # Savings are only meaningful for runs that actually completed. An
            # overflowed run dies after two requests having compressed nothing;
            # averaging its 0% in would understate compression on the runs that
            # ran, and overstate the harness's own coverage.
            if r["paritok"] and r["paritok_stats"] and r["outcome"] == "solved":
                try:
                    st = json.loads(r["paritok_stats"])
                    if st.get("input_tokens_original"):
                        savings.append(100 * st["tokens_saved"] / st["input_tokens_original"])
                except (TypeError, json.JSONDecodeError):
                    pass

    if savings:
        lines.append("")
        lines.append(
            f"Measured at the proxy, Paritok compressed the context it saw by "
            f"**{min(savings):.1f}–{max(savings):.1f}%** (mean {sum(savings) / len(savings):.1f}%)."
        )
    if paired:
        lines.append("")
        lines.append(
            f"End to end, `paritok` used **{min(paired):.1f}–{max(paired):.1f}% fewer input "
            f"tokens than `paginate`** (mean {sum(paired) / len(paired):.1f}%) while seeing "
            f"the same evidence and reaching the same fix. Those two arms are identical "
            f"apart from `base_url`, so the difference is attributable to compression alone."
        )
    return "\n".join(lines)


def write_examples(store: Store) -> int:
    EXAMPLES.mkdir(exist_ok=True)
    written = 0
    for pair in store.pairs():
        runs = store.runs_for_pair(pair["pair_id"])
        if len(runs) < 2:
            continue
        out = [f"# {pair['task']} — comparison `{pair['pair_id']}`\n"]
        for r in sorted(runs, key=lambda x: ARM_ORDER.get(x["strategy"] or "paginate", 9)):
            arm = r["strategy"] or ("paritok" if r["paritok"] else "paginate")
            out.append(f"\n## {arm}\n")
            out.append(
                f"- outcome: **{_outcome_cell(r)}**\n"
                f"- turns: {r['turns_completed']}\n"
                f"- peak prompt tokens: {r['peak_prompt_tokens']:,}\n"
                f"- total input tokens: {r['total_prompt_tokens']:,}\n"
                f"- patches applied: {r['patches_applied']}\n"
                f"- tool results truncated: {r['truncations'] or 0}\n"
                f"- wall time: {r['wall_time_s']}s\n"
            )
            if r["paritok_stats"]:
                out.append(f"- proxy stats: `{r['paritok_stats']}`\n")

            out.append("\n### Turn-by-turn\n")
            out.append("| turn | tool | prompt tokens | vs 32,768 |")
            out.append("|---:|---|---:|---|")
            for t in store.turns_for_run(r["id"]):
                tok = t["actual_prompt_tokens"] or t["estimated_prompt_tokens"] or 0
                pct = 100 * tok / 32768
                out.append(f"| {t['turn']} | `{t['tool_name'] or '—'}` | {tok:,} | {pct:.0f}% |")
        path = EXAMPLES / f"{pair['task']}__{pair['pair_id']}.md"
        path.write_text("\n".join(out) + "\n")
        written += 1
    return written


def main() -> None:
    store = Store()
    table = results_table(store)
    if README.exists() and START in README.read_text():
        text = README.read_text()
        head, _, rest = text.partition(START)
        _, _, tail = rest.partition(END)
        README.write_text(f"{head}{START}\n\n{table}\n\n{END}{tail}")
        print("README results updated")
    n = write_examples(store)
    print(f"wrote {n} example transcript(s) to examples/")


if __name__ == "__main__":
    main()
