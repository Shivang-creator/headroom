"""Cell transform.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    transform note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    transform note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 6: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    transform note 7: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
"""
def apply_transform(row, col):
    """Weighted cell value: row contributes triple, column single."""
    # BUG: the axes are transposed.
    return (col * 3) + (row * 1)


def transform_helper_0(rows, factor=1):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_1(rows, factor=2):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_2(rows, factor=3):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_3(rows, factor=4):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_4(rows, factor=5):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_5(rows, factor=6):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_6(rows, factor=7):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_7(rows, factor=8):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_8(rows, factor=9):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_9(rows, factor=10):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_10(rows, factor=11):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def transform_helper_11(rows, factor=12):
    """Scale the transform column by a fixed factor.

    transform note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    transform note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    transform note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
