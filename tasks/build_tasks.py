"""Generates the seeded task repos.

Design note that matters for the comparison: the failing assertion must NOT
point at the buggy line. If a traceback names the culprit, a competent agent
reads one file and fixes it in three turns — never accumulating enough context
for the ceiling to bite, and the A/B proves nothing.

So each task asserts on *final pipeline output*. The agent has to trace the
data path across several modules to find where the value goes wrong, which is
both realistic and what actually grows the context window.

Run:  python tasks/build_tasks.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent

FILLER_DOC = '"""{title}\n\n{body}\n"""\n'


def _prose(n: int, seed: str) -> str:
    """Deterministic filler docs — bulk without pretending to be meaningful."""
    lines = []
    for i in range(n):
        lines.append(
            f"    {seed} note {i}: this helper participates in the reporting "
            f"pipeline and is retained for backwards compatibility with the "
            f"v{i % 4}.x report schema."
        )
    return "\n".join(lines)


def _helpers(prefix: str, count: int) -> str:
    out = []
    for i in range(count):
        out.append(
            f"def {prefix}_helper_{i}(rows, factor={i + 1}):\n"
            f'    """Scale the {prefix} column by a fixed factor.\n\n'
            f"{_prose(3, prefix)}\n"
            f'    """\n'
            f"    return [r * factor for r in rows]\n"
        )
    return "\n\n".join(out)


# --------------------------------------------------------------------------
# Task 1 — the mean is computed one element too wide, three layers down.
# --------------------------------------------------------------------------
TASK1 = {
    "name": "task01_report_mean",
    "brief": (
        "The reporting pipeline in this repo produces a summary report from CSV rows. "
        "`python -m pytest -q` fails: the summary's average column is wrong for every "
        "group. Find the cause and fix it. Do not modify the tests."
    ),
    "files": {
        "csvreport/__init__.py": "from .pipeline import build_report\n\n__all__ = ['build_report']\n",
        "csvreport/pipeline.py": (
            FILLER_DOC.format(title="Top-level report pipeline.", body=_prose(6, "pipeline"))
            + "from .loader import load_rows\n"
            "from .grouping import group_rows\n"
            "from .summary import summarise_groups\n"
            "from .formatting import render_report\n\n\n"
            "def build_report(raw, key, value_field):\n"
            '    """Load, group, summarise, render. The public entry point."""\n'
            "    rows = load_rows(raw)\n"
            "    groups = group_rows(rows, key)\n"
            "    summary = summarise_groups(groups, value_field)\n"
            "    return render_report(summary)\n\n\n"
            + _helpers("pipeline", 14)
        ),
        "csvreport/loader.py": (
            FILLER_DOC.format(title="Row loading and coercion.", body=_prose(6, "loader"))
            + "def load_rows(raw):\n"
            '    """Coerce raw dicts into typed rows."""\n'
            "    out = []\n"
            "    for item in raw:\n"
            "        row = dict(item)\n"
            "        for field in ('amount', 'qty', 'weight'):\n"
            "            if field in row:\n"
            "                row[field] = float(row[field])\n"
            "        out.append(row)\n"
            "    return out\n\n\n"
            + _helpers("loader", 16)
        ),
        "csvreport/grouping.py": (
            FILLER_DOC.format(title="Grouping strategies.", body=_prose(6, "grouping"))
            + "from collections import OrderedDict\n\n\n"
            "def group_rows(rows, key):\n"
            '    """Bucket rows by the value of `key`, preserving first-seen order."""\n'
            "    buckets = OrderedDict()\n"
            "    for row in rows:\n"
            "        buckets.setdefault(row[key], []).append(row)\n"
            "    return buckets\n\n\n"
            + _helpers("grouping", 16)
        ),
        "csvreport/summary.py": (
            FILLER_DOC.format(title="Per-group summary statistics.", body=_prose(6, "summary"))
            + "from .stats import mean, total\n\n\n"
            "def summarise_groups(groups, value_field):\n"
            '    """Produce {group: {total, average, count}} for each bucket."""\n'
            "    summary = {}\n"
            "    for name, rows in groups.items():\n"
            "        values = [r[value_field] for r in rows]\n"
            "        summary[name] = {\n"
            "            'total': total(values),\n"
            "            'average': mean(values),\n"
            "            'count': len(values),\n"
            "        }\n"
            "    return summary\n\n\n"
            + _helpers("summary", 15)
        ),
        # The bug lives here, and nothing in the traceback will mention it.
        "csvreport/stats.py": (
            FILLER_DOC.format(title="Numeric primitives.", body=_prose(6, "stats"))
            + "def total(values):\n"
            '    """Sum of values."""\n'
            "    return sum(values)\n\n\n"
            "def mean(values):\n"
            '    """Arithmetic mean of values."""\n'
            "    if not values:\n"
            "        return 0.0\n"
            "    # BUG: the denominator counts one element that is not there.\n"
            "    return total(values) / (len(values) + 1)\n\n\n"
            "def median(values):\n"
            '    """Middle value of a sorted copy."""\n'
            "    if not values:\n"
            "        return 0.0\n"
            "    ordered = sorted(values)\n"
            "    mid = len(ordered) // 2\n"
            "    if len(ordered) % 2:\n"
            "        return ordered[mid]\n"
            "    return (ordered[mid - 1] + ordered[mid]) / 2\n\n\n"
            + _helpers("stats", 15)
        ),
        "csvreport/formatting.py": (
            FILLER_DOC.format(title="Report rendering.", body=_prose(6, "formatting"))
            + "def render_report(summary):\n"
            '    """Render the summary dict into a list of display rows."""\n'
            "    rows = []\n"
            "    for name in summary:\n"
            "        s = summary[name]\n"
            "        rows.append({\n"
            "            'group': name,\n"
            "            'total': round(s['total'], 4),\n"
            "            'average': round(s['average'], 4),\n"
            "            'count': s['count'],\n"
            "        })\n"
            "    return rows\n\n\n"
            + _helpers("formatting", 16)
        ),
        "csvreport/validators.py": (
            FILLER_DOC.format(title="Input validation.", body=_prose(6, "validators"))
            + _helpers("validators", 20)
        ),
        "csvreport/filters.py": (
            FILLER_DOC.format(title="Row filters.", body=_prose(6, "filters"))
            + _helpers("filters", 20)
        ),
        "tests/test_report.py": (
            "from csvreport import build_report\n\n\n"
            "RAW = [\n"
            "    {'region': 'north', 'amount': '10'},\n"
            "    {'region': 'north', 'amount': '20'},\n"
            "    {'region': 'north', 'amount': '30'},\n"
            "    {'region': 'south', 'amount': '5'},\n"
            "    {'region': 'south', 'amount': '15'},\n"
            "]\n\n\n"
            "def test_totals_are_correct():\n"
            "    report = build_report(RAW, 'region', 'amount')\n"
            "    north = [r for r in report if r['group'] == 'north'][0]\n"
            "    assert north['total'] == 60.0\n\n\n"
            "def test_average_is_correct():\n"
            "    report = build_report(RAW, 'region', 'amount')\n"
            "    north = [r for r in report if r['group'] == 'north'][0]\n"
            "    assert north['average'] == 20.0\n\n\n"
            "def test_south_average_is_correct():\n"
            "    report = build_report(RAW, 'region', 'amount')\n"
            "    south = [r for r in report if r['group'] == 'south'][0]\n"
            "    assert south['average'] == 10.0\n\n\n"
            "def test_counts_are_correct():\n"
            "    report = build_report(RAW, 'region', 'amount')\n"
            "    assert {r['group']: r['count'] for r in report} == {'north': 3, 'south': 2}\n"
        ),
    },
}


# --------------------------------------------------------------------------
# Task 2 — three independent bugs across a wide repo, with verbose failures.
#
# Task 1 turned out to be too easy to be interesting: the agent grepped, read
# three files, and fixed it in nine turns, peaking at 7,013 tokens against a
# 32,768 ceiling. It never came close to overflowing, so it could not show
# whether compression buys anything beyond cost.
#
# What actually grows an agent's context is (a) breadth — more places the bug
# could be — and (b) verbose tool output. So this task has three unrelated bugs
# in different subsystems, and the tests assert on large structures, which makes
# pytest print big diffs. Those diffs are `log_output` blocks, which is Paritok's
# best case.
# --------------------------------------------------------------------------
def _wide_module(name: str, count: int) -> str:
    return (
        FILLER_DOC.format(title=f"{name} subsystem.", body=_prose(8, name))
        + _helpers(name, count)
    )


TASK2_MODULES = [
    "ingest", "normalise", "dedupe", "enrich", "scoring", "ranking",
    "bucketing", "windowing", "rollup", "emit", "audit", "retry",
    "backoff", "throttle", "cursor", "checkpoint",
]

TASK2 = {
    "name": "task02_pipeline_triage",
    "brief": (
        "This repo runs an event-processing pipeline. `python -m pytest -q` reports "
        "three separate failures across different subsystems. They are unrelated bugs. "
        "Find and fix all three so the whole suite passes. Do not modify the tests."
    ),
    "files": {
        "evpipe/__init__.py": "from .runner import process\n\n__all__ = ['process']\n",
        # Bug 1: off-by-one window boundary (exclusive where it should be inclusive).
        "evpipe/windows.py": (
            FILLER_DOC.format(title="Time-window assignment.", body=_prose(8, "windows"))
            + "def assign_window(ts, size):\n"
            '    """Return the window index a timestamp belongs to."""\n'
            "    # BUG: a timestamp exactly on a boundary belongs to the window it\n"
            "    # starts, not the one it ends.\n"
            "    return (ts - 1) // size\n\n\n"
            "def window_bounds(index, size):\n"
            '    """Inclusive start, exclusive end, of a window."""\n'
            "    return index * size, (index + 1) * size\n\n\n"
            + _helpers("windows", 12)
        ),
        # Bug 2: dedupe keeps the last occurrence instead of the first.
        "evpipe/dedupe.py": (
            FILLER_DOC.format(title="Deduplication.", body=_prose(8, "dedupe"))
            + "def dedupe(events, key='id'):\n"
            '    """Keep the FIRST occurrence of each key, preserving order."""\n'
            "    seen = {}\n"
            "    for ev in events:\n"
            "        # BUG: this overwrites, so the last occurrence wins.\n"
            "        seen[ev[key]] = ev\n"
            "    return list(seen.values())\n\n\n"
            + _helpers("dedupe", 12)
        ),
        # Bug 3: score normalisation divides by max instead of the range.
        "evpipe/scoring.py": (
            FILLER_DOC.format(title="Scoring and normalisation.", body=_prose(8, "scoring"))
            + "def normalise(scores):\n"
            '    """Min-max normalise scores into 0..1."""\n'
            "    if not scores:\n"
            "        return []\n"
            "    lo, hi = min(scores), max(scores)\n"
            "    if hi == lo:\n"
            "        return [0.0 for _ in scores]\n"
            "    # BUG: min-max normalisation subtracts the minimum first.\n"
            "    return [s / hi for s in scores]\n\n\n"
            + _helpers("scoring", 12)
        ),
        "evpipe/runner.py": (
            FILLER_DOC.format(title="Pipeline runner.", body=_prose(8, "runner"))
            + "from .dedupe import dedupe\n"
            "from .windows import assign_window\n"
            "from .scoring import normalise\n\n\n"
            "def process(events, window_size=10):\n"
            '    """Dedupe, window, and normalise a batch of events."""\n'
            "    unique = dedupe(events)\n"
            "    for ev in unique:\n"
            "        ev['window'] = assign_window(ev['ts'], window_size)\n"
            "    norm = normalise([ev['score'] for ev in unique])\n"
            "    for ev, n in zip(unique, norm):\n"
            "        ev['norm'] = round(n, 4)\n"
            "    return unique\n\n\n"
            + _helpers("runner", 12)
        ),
        "tests/test_pipeline.py": (
            "from evpipe import process\n\n\n"
            "EVENTS = [\n"
            "    {'id': 'a', 'ts': 10, 'score': 20, 'tag': 'first-a'},\n"
            "    {'id': 'b', 'ts': 11, 'score': 40, 'tag': 'first-b'},\n"
            "    {'id': 'a', 'ts': 12, 'score': 99, 'tag': 'second-a'},\n"
            "    {'id': 'c', 'ts': 20, 'score': 60, 'tag': 'first-c'},\n"
            "]\n\n\n"
            "def test_dedupe_keeps_first_occurrence():\n"
            "    out = process(EVENTS)\n"
            "    tags = {e['id']: e['tag'] for e in out}\n"
            "    assert tags == {'a': 'first-a', 'b': 'first-b', 'c': 'first-c'}\n\n\n"
            "def test_window_boundaries_are_inclusive_at_start():\n"
            "    out = process(EVENTS)\n"
            "    windows = {e['id']: e['window'] for e in out}\n"
            "    assert windows == {'a': 1, 'b': 1, 'c': 2}\n\n\n"
            "def test_scores_are_min_max_normalised():\n"
            "    out = process(EVENTS)\n"
            "    norms = {e['id']: e['norm'] for e in out}\n"
            "    assert norms == {'a': 0.0, 'b': 0.5, 'c': 1.0}\n"
        ),
    },
}

# Bulk out task 2 so the search space is genuinely wide.
for _name in TASK2_MODULES:
    TASK2["files"][f"evpipe/{_name}_support.py"] = _wide_module(_name, 18)


# --------------------------------------------------------------------------
# Task 3 — one enormous tool result.
#
# Tasks 1 and 2 both stayed under the ceiling: a competent agent greps, reads
# three or four files, and finishes around 17,000 tokens. Breadth alone does not
# overflow a 32,768-token window.
#
# What does is a single huge tool result. A parameterised suite with a few
# hundred failing cases emits tens of thousands of tokens from ONE `pytest`
# call — before the agent has read a single source file. This is not a contrived
# shape; it is what CI triage actually looks like.
#
# Without compression the agent has exactly two options: truncate the output and
# hope the informative part survived, or die. That trade-off is the entire
# argument for compression, so the task is built to force it.
# --------------------------------------------------------------------------
TASK3 = {
    "name": "task03_verbose_suite",
    # The instruction to review the *whole* failure set is the point. Left to
    # itself the agent self-limits — it pipes pytest through `head`, reads
    # selectively, and never approaches the ceiling. That is competent, and it
    # is also context engineering a human had to do by hand.
    #
    # "Show me all the failures before you change anything" is an ordinary thing
    # to ask of a coding agent, and it is what forces the full 82,000-token tool
    # result into the window. This task measures what that request costs you.
    "brief": (
        "This repo's test suite is failing across a few hundred parameterised cases.\n\n"
        "Run the FULL test suite with `python -m pytest -q` and review the complete "
        "failure output before changing anything — do not pipe it through `head`, "
        "`tail`, or `-x`, and do not sample a subset. The failure pattern across all "
        "cases is what identifies the root cause.\n\n"
        "Then find the single root cause and fix it. Do not modify the tests."
    ),
    "files": {
        "gridcalc/__init__.py": "from .grid import evaluate\n\n__all__ = ['evaluate']\n",
        "gridcalc/grid.py": (
            FILLER_DOC.format(title="Grid evaluation.", body=_prose(8, "grid"))
            + "from .transform import apply_transform\n\n\n"
            "def evaluate(rows, cols):\n"
            '    """Build a rows x cols grid of transformed cell values."""\n'
            "    return [[apply_transform(r, c) for c in range(cols)] for r in range(rows)]\n\n\n"
            + _helpers("grid", 12)
        ),
        # The bug: row and column are swapped in the weighting term.
        "gridcalc/transform.py": (
            FILLER_DOC.format(title="Cell transform.", body=_prose(8, "transform"))
            + "def apply_transform(row, col):\n"
            '    """Weighted cell value: row contributes triple, column single."""\n'
            "    # BUG: the weights are attached to the wrong axes.\n"
            "    return (col * 3) + (row * 1)\n\n\n"
            + _helpers("transform", 12)
        ),
        "tests/test_grid.py": (
            "import pytest\n\n"
            "from gridcalc import evaluate\n\n\n"
            "def expected(row, col):\n"
            "    return (row * 3) + (col * 1)\n\n\n"
            "CASES = [(r, c) for r in range(18) for c in range(18)]\n\n\n"
            "@pytest.mark.parametrize('row,col', CASES)\n"
            "def test_every_cell_is_weighted_correctly(row, col):\n"
            "    grid = evaluate(18, 18)\n"
            "    context = {\n"
            "        'row': row, 'col': col,\n"
            "        'row_values': grid[row],\n"
            "        'col_values': [grid[r][col] for r in range(18)],\n"
            "    }\n"
            "    assert grid[row][col] == expected(row, col), context\n"
        ),
    },
}


# --------------------------------------------------------------------------
# Task 4 — the full-audit workflow, where paging itself fills the window.
#
# Tasks 1-3 all fit under the ceiling because the agent stops early: it spots
# the failure pattern after a page or two and goes straight to the fix. That is
# good behaviour, and it is why we could not honestly claim "the agent dies
# without compression."
#
# But "characterise every failure before you touch the code" is a real triage
# instruction — you give it when you need to know a fix addresses the whole
# failure set rather than the first symptom. It forces the agent to page through
# everything, and *that* is what fills a 32,768-token window: 484 failing cases
# is ~40 pages at ~3,100 tokens each.
#
# This is where compression stops being a discount and starts being the thing
# that makes the workflow possible. The paginate arm should exhaust the window
# partway through the audit; the paritok arm should compress the pages it has
# already read and keep going.
# --------------------------------------------------------------------------
TASK4 = {
    "name": "task04_full_audit",
    "brief": (
        "This repo's grid evaluator is failing across every parameterised case.\n\n"
        "Before changing any code, AUDIT THE COMPLETE FAILURE SET:\n"
        "  1. Run `python -m pytest -q` to get the failures.\n"
        "  2. The output is paginated. Call next_page repeatedly until it reports "
        "that no pages remain. Do not stop early, do not sample, and do not pipe "
        "the command through head/tail or use -x.\n"
        "  3. Only once you have seen every page, state how many cases failed and "
        "whether they share a single root cause.\n\n"
        "Then fix the root cause and confirm the suite passes. Do not modify the tests.\n\n"
        "This matters because a fix that resolves the first few failures but not the "
        "rest is worse than no fix — it looks green locally and breaks in CI."
    ),
    "files": {
        "gridcalc/__init__.py": "from .grid import evaluate\n\n__all__ = ['evaluate']\n",
        "gridcalc/grid.py": (
            FILLER_DOC.format(title="Grid evaluation.", body=_prose(8, "grid"))
            + "from .transform import apply_transform\n\n\n"
            "def evaluate(rows, cols):\n"
            '    """Build a rows x cols grid of transformed cell values."""\n'
            "    return [[apply_transform(r, c) for c in range(cols)] for r in range(rows)]\n\n\n"
            + _helpers("grid", 12)
        ),
        "gridcalc/transform.py": (
            FILLER_DOC.format(title="Cell transform.", body=_prose(8, "transform"))
            + "def apply_transform(row, col):\n"
            '    """Weighted cell value: row contributes triple, column single."""\n'
            "    # BUG: the axes are transposed.\n"
            "    return (col * 3) + (row * 1)\n\n\n"
            + _helpers("transform", 12)
        ),
        "tests/test_grid.py": (
            "import pytest\n\n"
            "from gridcalc import evaluate\n\n\n"
            "def expected(row, col):\n"
            "    return (row * 3) + (col * 1)\n\n\n"
            "CASES = [(r, c) for r in range(22) for c in range(22)]\n\n\n"
            "@pytest.mark.parametrize('row,col', CASES)\n"
            "def test_every_cell_is_weighted_correctly(row, col):\n"
            "    grid = evaluate(22, 22)\n"
            "    context = {\n"
            "        'row': row, 'col': col,\n"
            "        'row_values': grid[row],\n"
            "        'col_values': [grid[r][col] for r in range(22)],\n"
            "    }\n"
            "    assert grid[row][col] == expected(row, col), context\n"
        ),
    },
}


def write_task(spec: dict) -> Path:
    root = HERE / spec["name"]
    if root.exists():
        shutil.rmtree(root)
    for rel, content in spec["files"].items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (root / "TASK.md").write_text(f"# {spec['name']}\n\n{spec['brief']}\n")
    return root


def main() -> None:
    for spec in (TASK1, TASK2, TASK3, TASK4):
        root = write_task(spec)
        total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
        print(f"{spec['name']}: {total:,} bytes  (~{int(total / 2.9):,} tokens if fully read)")


if __name__ == "__main__":
    main()
