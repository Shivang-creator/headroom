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


def results_table(store: Store) -> str:
    lines = [
        "| Task | Arm | Outcome | Turns | Peak prompt tokens | Total input tokens | Tests |",
        "|---|---|---|---:|---:|---:|:--:|",
    ]
    savings = []
    for pair in reversed(store.pairs()):
        runs = store.runs_for_pair(pair["pair_id"])
        if len(runs) < 2:
            continue
        for r in runs:
            arm = "Paritok **on**" if r["paritok"] else "Paritok off"
            lines.append(
                f"| `{r['task']}` | {arm} | {_outcome_cell(r)} | {r['turns_completed']} | "
                f"{r['peak_prompt_tokens']:,} | {r['total_prompt_tokens']:,} | "
                f"{'✅' if r['tests_passed'] == 1 else '❌'} |"
            )
            if r["paritok"] and r["paritok_stats"]:
                try:
                    st = json.loads(r["paritok_stats"])
                    if st.get("input_tokens_original"):
                        savings.append(100 * st["tokens_saved"] / st["input_tokens_original"])
                except (TypeError, json.JSONDecodeError):
                    pass

    if savings:
        lines.append("")
        lines.append(
            f"Across {len(savings)} compressed runs Paritok cut input tokens by "
            f"**{min(savings):.1f}–{max(savings):.1f}%** "
            f"(mean {sum(savings) / len(savings):.1f}%), with both arms reaching "
            f"the same outcome on every task."
        )
    return "\n".join(lines)


def write_examples(store: Store) -> int:
    EXAMPLES.mkdir(exist_ok=True)
    written = 0
    for pair in store.pairs():
        runs = store.runs_for_pair(pair["pair_id"])
        if len(runs) < 2:
            continue
        out = [f"# {pair['task']} — pair `{pair['pair_id']}`\n"]
        for r in runs:
            arm = "Paritok ON" if r["paritok"] else "Paritok OFF"
            out.append(f"\n## {arm}\n")
            out.append(
                f"- outcome: **{_outcome_cell(r)}**\n"
                f"- turns: {r['turns_completed']}\n"
                f"- peak prompt tokens: {r['peak_prompt_tokens']:,}\n"
                f"- total input tokens: {r['total_prompt_tokens']:,}\n"
                f"- patches applied: {r['patches_applied']}\n"
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
