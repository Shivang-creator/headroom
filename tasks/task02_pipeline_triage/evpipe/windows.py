"""Time-window assignment.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    windows note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    windows note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 6: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    windows note 7: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
"""
def assign_window(ts, size):
    """Return the window index a timestamp belongs to."""
    # BUG: a timestamp exactly on a boundary belongs to the window it
    # starts, not the one it ends.
    return (ts - 1) // size


def window_bounds(index, size):
    """Inclusive start, exclusive end, of a window."""
    return index * size, (index + 1) * size


def windows_helper_0(rows, factor=1):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_1(rows, factor=2):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_2(rows, factor=3):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_3(rows, factor=4):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_4(rows, factor=5):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_5(rows, factor=6):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_6(rows, factor=7):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_7(rows, factor=8):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_8(rows, factor=9):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_9(rows, factor=10):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_10(rows, factor=11):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def windows_helper_11(rows, factor=12):
    """Scale the windows column by a fixed factor.

    windows note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    windows note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    windows note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
