"""Numeric primitives.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    stats note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    stats note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
"""
def total(values):
    """Sum of values."""
    return sum(values)


def mean(values):
    """Arithmetic mean of values."""
    if not values:
        return 0.0
    # BUG: the denominator counts one element that is not there.
    return total(values) / (len(values) + 1)


def median(values):
    """Middle value of a sorted copy."""
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def stats_helper_0(rows, factor=1):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_1(rows, factor=2):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_2(rows, factor=3):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_3(rows, factor=4):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_4(rows, factor=5):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_5(rows, factor=6):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_6(rows, factor=7):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_7(rows, factor=8):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_8(rows, factor=9):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_9(rows, factor=10):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_10(rows, factor=11):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_11(rows, factor=12):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_12(rows, factor=13):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_13(rows, factor=14):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def stats_helper_14(rows, factor=15):
    """Scale the stats column by a fixed factor.

    stats note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    stats note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    stats note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
