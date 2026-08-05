"""Tests for the harness itself.

The harness produces the numbers the whole submission rests on, so the parts
that could silently corrupt a result — path sandboxing, patch application,
pagination boundaries, overflow parsing, verification — are tested directly.

An earlier version of `_verify` ran `pytest | tail -5` and read *tail's* exit
status, so every run reported green regardless of outcome. That class of bug is
invisible in the output and fatal to the conclusions, which is what these guard
against.

    .venv/bin/python -m pytest tests/ -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from headroom.config import ARMS, UPSTREAM_CONTEXT_LIMIT, RunConfig  # noqa: E402
from headroom.governor import (  # noqa: E402
    Governor, TurnRecord, estimate_tokens, is_overflow, parse_overflow,
)
from headroom.store import Store  # noqa: E402
from headroom.tools import PAGE_CHARS, Toolbox  # noqa: E402


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text("def f(x):\n    return x + 1\n")
    (tmp_path / "notes.txt").write_text("hello\n")
    return tmp_path


@pytest.fixture
def tb(repo: Path) -> Toolbox:
    return Toolbox(repo)


# --------------------------------------------------------------------------
# Path sandboxing — the agent runs shell commands, so escapes matter.
# --------------------------------------------------------------------------
class TestSandbox:
    def test_reads_inside_repo(self, tb):
        assert "def f(x)" in tb.call("read_file", {"path": "pkg/mod.py"})

    @pytest.mark.parametrize("escape", ["../etc/passwd", "../../../../etc/passwd", "pkg/../../outside"])
    def test_rejects_paths_outside_repo(self, tb, escape):
        out = tb.call("read_file", {"path": escape})
        assert "escapes the task repo" in out or "no such file" in out

    def test_absolute_path_outside_is_rejected(self, tb):
        out = tb.call("read_file", {"path": "/etc/passwd"})
        assert "escapes the task repo" in out

    def test_unknown_tool_is_reported_not_raised(self, tb):
        assert "unknown tool" in tb.call("definitely_not_a_tool", {})

    def test_bad_arguments_are_reported_not_raised(self, tb):
        assert "ERROR" in tb.call("read_file", {"wrong_kwarg": 1})


# --------------------------------------------------------------------------
# apply_patch — a wrong patch silently applied would invalidate a whole run.
# --------------------------------------------------------------------------
class TestApplyPatch:
    def test_applies_and_counts(self, tb, repo):
        out = tb.call("apply_patch", {"path": "pkg/mod.py", "old": "x + 1", "new": "x + 2"})
        assert "Patched" in out
        assert (repo / "pkg" / "mod.py").read_text() == "def f(x):\n    return x + 2\n"
        assert tb.patches_applied == 1

    def test_refuses_when_target_missing(self, tb, repo):
        out = tb.call("apply_patch", {"path": "pkg/mod.py", "old": "nope", "new": "x"})
        assert "not found" in out
        assert tb.patches_applied == 0
        assert "x + 1" in (repo / "pkg" / "mod.py").read_text()

    def test_refuses_ambiguous_match(self, tb, repo):
        (repo / "dup.py").write_text("a = 1\na = 1\n")
        out = tb.call("apply_patch", {"path": "dup.py", "old": "a = 1", "new": "a = 2"})
        assert "appears 2 times" in out
        assert tb.patches_applied == 0
        assert (repo / "dup.py").read_text() == "a = 1\na = 1\n"


# --------------------------------------------------------------------------
# Pagination — this is what keeps blocks inside Paritok's working band.
# --------------------------------------------------------------------------
class TestPagination:
    def test_small_output_is_not_paginated(self, tb):
        out = tb.call("read_file", {"path": "notes.txt"})
        assert "page 1 of" not in out
        assert tb.call("next_page", {}) == "No further pages."

    def test_large_output_paginates_and_reassembles(self, tb, repo):
        (repo / "big.txt").write_text("\n".join(f"line {i:06d}" for i in range(8000)))
        first = tb.call("read_file", {"path": "big.txt"})
        assert "page 1 of" in first

        pages, guard = 1, 0
        while guard < 500:
            guard += 1
            nxt = tb.call("next_page", {})
            if nxt == "No further pages.":
                break
            pages += 1
        assert pages > 1
        assert "final page" in nxt or nxt == "No further pages."

    def test_every_page_fits_the_compressor_band(self, tb, repo):
        """Each page must stay under the ~6k-token passthrough cliff."""
        (repo / "big.txt").write_text("x" * (PAGE_CHARS * 6))
        out = tb.call("read_file", {"path": "big.txt"})
        # page body + the pagination note; the note is short by construction
        assert len(out) < PAGE_CHARS + 200
        while True:
            nxt = tb.call("next_page", {})
            if nxt == "No further pages.":
                break
            assert len(nxt) < PAGE_CHARS + 200

    def test_next_page_tolerates_unexpected_arguments(self, tb, repo):
        """Models pass stray args. That must not surface as a tool error."""
        (repo / "big.txt").write_text("y" * (PAGE_CHARS * 3))
        tb.call("read_file", {"path": "big.txt"})
        out = tb.call("next_page", {"page": 2})
        assert "ERROR" not in out

    def test_new_pagination_replaces_the_previous_one(self, tb, repo):
        (repo / "a.txt").write_text("a" * (PAGE_CHARS * 3))
        (repo / "b.txt").write_text("b" * (PAGE_CHARS * 3))
        tb.call("read_file", {"path": "a.txt"})
        tb.call("read_file", {"path": "b.txt"})
        assert "b" in tb.call("next_page", {})


# --------------------------------------------------------------------------
# run_bash — exit codes are how we decide whether a run actually succeeded.
# --------------------------------------------------------------------------
class TestRunBash:
    def test_reports_exit_zero(self, tb):
        assert "(exit 0)" in tb.call("run_bash", {"cmd": "true"})

    def test_reports_nonzero_exit(self, tb):
        assert "(exit 1)" in tb.call("run_bash", {"cmd": "false"})

    def test_exit_code_survives_pagination(self, tb):
        """The regression that made every run look green.

        `pytest | tail` reports tail's status. The exit marker must appear on
        page 1, or verification silently reads the wrong number.
        """
        out = tb.call("run_bash", {"cmd": "python3 -c \"print('z'*400000)\"; exit 3"})
        assert "(exit 3)" in out

    def test_bare_python_resolves(self, tb):
        """macOS has no bare `python`; the agent should not have to know that."""
        assert "(exit 0)" in tb.call("run_bash", {"cmd": "python -c 'pass'"})


# --------------------------------------------------------------------------
# Governor — an overflow must be recorded as a measurement, not just a failure.
# --------------------------------------------------------------------------
class TestGovernor:
    ERR = (
        '{"error":{"message":"Maximum context length for model \'zai-org/GLM-5.1\' '
        "allowed on your plan is 32768 tokens. Your prompt has 38435 tokens, which "
        'exceeds the maximum context length limit by 5667 tokens.",'
        '"code":"context_length_exceeded"}}'
    )

    def test_detects_overflow(self):
        assert is_overflow(self.ERR)
        assert not is_overflow('{"error":{"message":"This model is busy"}}')

    def test_extracts_exact_token_counts(self):
        prompt, limit = parse_overflow(self.ERR)
        assert prompt == 38435
        assert limit == 32768

    def test_records_overflow_and_adopts_reported_limit(self):
        g = Governor(limit=999)
        g.record_overflow(7, self.ERR)
        assert g.overflowed_at_turn == 7
        assert g.overflow_tokens == 38435
        assert g.limit == 32768

    def test_parse_returns_none_on_unrelated_error(self):
        assert parse_overflow("some other failure") == (None, None)

    def test_actual_tokens_win_over_estimates(self):
        rec = TurnRecord(1, "read_file", estimated_prompt_tokens=9999, actual_prompt_tokens=1234)
        assert rec.prompt_tokens == 1234

    def test_headroom_never_goes_negative(self):
        rec = TurnRecord(1, None, estimated_prompt_tokens=UPSTREAM_CONTEXT_LIMIT * 3)
        assert rec.headroom_pct == 0.0

    def test_totals_and_peak(self):
        g = Governor()
        g.record(TurnRecord(1, None, 100, actual_prompt_tokens=100))
        g.record(TurnRecord(2, None, 300, actual_prompt_tokens=300))
        assert g.total_prompt_tokens == 400
        assert g.peak_prompt_tokens == 300

    def test_bar_marks_overflow(self):
        g = Governor()
        assert "OVER" in g.bar(UPSTREAM_CONTEXT_LIMIT + 1)
        assert "OVER" not in g.bar(1000)

    def test_estimate_grows_with_content(self):
        small = estimate_tokens([{"role": "user", "content": "hi"}])
        large = estimate_tokens([{"role": "user", "content": "hi" * 5000}])
        assert large > small > 0


# --------------------------------------------------------------------------
# Config — the arms must differ in exactly one thing.
# --------------------------------------------------------------------------
class TestRunConfig:
    def test_only_base_url_differs_between_paginate_and_paritok(self):
        """These two arms must be identical apart from where requests go —
        that is what makes the compression number attributable."""
        off = RunConfig(paritok=False, strategy="paginate")
        on = RunConfig(paritok=True, strategy="paritok")
        assert off.base_url != on.base_url
        assert "127.0.0.1:8080" in on.base_url
        assert off.model == on.model
        assert off.temperature == on.temperature == 0.0
        assert off.paginate == on.paginate is True
        assert off.effective_tool_budget == on.effective_tool_budget

    def test_labels_are_distinct(self):
        labels = {RunConfig(paritok=False, strategy=s).label for s in ARMS}
        assert labels == set(ARMS)

    def test_truncate_arm_does_not_paginate_and_runs_a_smaller_budget(self):
        t = RunConfig(paritok=False, strategy="truncate")
        p = RunConfig(paritok=False, strategy="paginate")
        assert t.paginate is False and p.paginate is True
        assert t.effective_tool_budget < p.effective_tool_budget

    def test_only_the_paritok_arm_routes_through_the_proxy(self):
        assert "127.0.0.1" not in RunConfig(paritok=False, strategy="truncate").base_url
        assert "127.0.0.1" not in RunConfig(paritok=False, strategy="paginate").base_url
        assert "127.0.0.1" in RunConfig(paritok=True, strategy="paritok").base_url


class TestTruncationStrategy:
    """The truncating arm must lose content, and must say so."""

    def test_truncates_instead_of_paginating(self, repo):
        tb = Toolbox(repo, max_tool_output=5_000, paginate=False)
        (repo / "big.txt").write_text("q" * 40_000)
        out = tb.call("read_file", {"path": "big.txt"})
        assert "page 1 of" not in out
        assert "TRUNCATED" in out
        assert tb.truncations == 1
        assert tb.call("next_page", {}) == "No further pages."

    def test_truncation_is_declared_not_silent(self, repo):
        """A silent cut lets the agent conclude confidently from evidence it
        never saw. It must know the tail is missing."""
        tb = Toolbox(repo, max_tool_output=5_000, paginate=False)
        (repo / "big.txt").write_text("q" * 40_000)
        out = tb.call("read_file", {"path": "big.txt"})
        assert "more characters were dropped" in out

    def test_paginating_arm_never_truncates(self, repo):
        tb = Toolbox(repo, max_tool_output=120_000, paginate=True)
        (repo / "big.txt").write_text("q" * 40_000)
        tb.call("read_file", {"path": "big.txt"})
        while tb.call("next_page", {}) != "No further pages.":
            pass
        assert tb.truncations == 0


# --------------------------------------------------------------------------
# Store — the dashboard and exporter both read this; the schema is the contract.
# --------------------------------------------------------------------------
class TestStore:
    def test_roundtrip(self, tmp_path):
        s = Store(tmp_path / "t.db")
        rid = s.start_run("pair1", "task01", True, "m")
        s.add_turn(rid, TurnRecord(1, "read_file", 100, actual_prompt_tokens=90), {"path": "a"})
        s.save_transcript(rid, [{"role": "user", "content": "hi"}])
        s.finish_run(rid, outcome="solved", tests_passed=1, turns_completed=1)

        turns = s.turns_for_run(rid)
        assert len(turns) == 1 and turns[0]["actual_prompt_tokens"] == 90
        assert len(s.transcript_for_run(rid)) == 1

    def test_pairs_excludes_incomplete_runs(self, tmp_path):
        """A single-arm run has nothing to compare and must not reach the UI."""
        s = Store(tmp_path / "t.db")
        s.start_run("solo", "task01", True, "m")
        s.start_run("both", "task01", False, "m")
        s.start_run("both", "task01", True, "m")
        ids = {p["pair_id"] for p in s.pairs()}
        assert ids == {"both"}

    def test_runs_for_pair_orders_off_then_on(self, tmp_path):
        s = Store(tmp_path / "t.db")
        s.start_run("p", "t", True, "m")
        s.start_run("p", "t", False, "m")
        assert [r["paritok"] for r in s.runs_for_pair("p")] == [0, 1]
