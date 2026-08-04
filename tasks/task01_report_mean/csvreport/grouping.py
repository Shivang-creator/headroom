"""Grouping strategies.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    grouping note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    grouping note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
"""
from collections import OrderedDict


def group_rows(rows, key):
    """Bucket rows by the value of `key`, preserving first-seen order."""
    buckets = OrderedDict()
    for row in rows:
        buckets.setdefault(row[key], []).append(row)
    return buckets


def grouping_helper_0(rows, factor=1):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_1(rows, factor=2):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_2(rows, factor=3):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_3(rows, factor=4):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_4(rows, factor=5):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_5(rows, factor=6):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_6(rows, factor=7):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_7(rows, factor=8):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_8(rows, factor=9):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_9(rows, factor=10):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_10(rows, factor=11):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_11(rows, factor=12):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_12(rows, factor=13):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_13(rows, factor=14):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_14(rows, factor=15):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grouping_helper_15(rows, factor=16):
    """Scale the grouping column by a fixed factor.

    grouping note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grouping note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grouping note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
