"""Grid evaluation.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    grid note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    grid note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 6: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    grid note 7: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
"""
from .transform import apply_transform


def evaluate(rows, cols):
    """Build a rows x cols grid of transformed cell values."""
    return [[apply_transform(r, c) for c in range(cols)] for r in range(rows)]


def grid_helper_0(rows, factor=1):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_1(rows, factor=2):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_2(rows, factor=3):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_3(rows, factor=4):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_4(rows, factor=5):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_5(rows, factor=6):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_6(rows, factor=7):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_7(rows, factor=8):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_8(rows, factor=9):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_9(rows, factor=10):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_10(rows, factor=11):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def grid_helper_11(rows, factor=12):
    """Scale the grid column by a fixed factor.

    grid note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    grid note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    grid note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
