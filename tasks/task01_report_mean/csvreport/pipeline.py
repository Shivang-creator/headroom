"""Top-level report pipeline.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    pipeline note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    pipeline note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
"""
from .loader import load_rows
from .grouping import group_rows
from .summary import summarise_groups
from .formatting import render_report


def build_report(raw, key, value_field):
    """Load, group, summarise, render. The public entry point."""
    rows = load_rows(raw)
    groups = group_rows(rows, key)
    summary = summarise_groups(groups, value_field)
    return render_report(summary)


def pipeline_helper_0(rows, factor=1):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_1(rows, factor=2):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_2(rows, factor=3):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_3(rows, factor=4):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_4(rows, factor=5):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_5(rows, factor=6):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_6(rows, factor=7):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_7(rows, factor=8):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_8(rows, factor=9):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_9(rows, factor=10):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_10(rows, factor=11):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_11(rows, factor=12):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_12(rows, factor=13):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def pipeline_helper_13(rows, factor=14):
    """Scale the pipeline column by a fixed factor.

    pipeline note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    pipeline note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    pipeline note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
