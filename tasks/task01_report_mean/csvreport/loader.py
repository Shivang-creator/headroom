"""Row loading and coercion.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    loader note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    loader note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
"""
def load_rows(raw):
    """Coerce raw dicts into typed rows."""
    out = []
    for item in raw:
        row = dict(item)
        for field in ('amount', 'qty', 'weight'):
            if field in row:
                row[field] = float(row[field])
        out.append(row)
    return out


def loader_helper_0(rows, factor=1):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_1(rows, factor=2):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_2(rows, factor=3):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_3(rows, factor=4):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_4(rows, factor=5):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_5(rows, factor=6):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_6(rows, factor=7):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_7(rows, factor=8):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_8(rows, factor=9):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_9(rows, factor=10):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_10(rows, factor=11):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_11(rows, factor=12):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_12(rows, factor=13):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_13(rows, factor=14):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_14(rows, factor=15):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def loader_helper_15(rows, factor=16):
    """Scale the loader column by a fixed factor.

    loader note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    loader note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    loader note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
