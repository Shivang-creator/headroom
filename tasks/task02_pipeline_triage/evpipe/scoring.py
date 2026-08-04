"""Scoring and normalisation.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    scoring note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    scoring note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 6: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    scoring note 7: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
"""
def normalise(scores):
    """Min-max normalise scores into 0..1."""
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return [0.0 for _ in scores]
    # BUG: min-max normalisation subtracts the minimum first.
    return [s / hi for s in scores]


def scoring_helper_0(rows, factor=1):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_1(rows, factor=2):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_2(rows, factor=3):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_3(rows, factor=4):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_4(rows, factor=5):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_5(rows, factor=6):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_6(rows, factor=7):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_7(rows, factor=8):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_8(rows, factor=9):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_9(rows, factor=10):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_10(rows, factor=11):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def scoring_helper_11(rows, factor=12):
    """Scale the scoring column by a fixed factor.

    scoring note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    scoring note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    scoring note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
