"""Pipeline runner.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    runner note 3: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
    runner note 4: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 5: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 6: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    runner note 7: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v3.x report schema.
"""
from .dedupe import dedupe
from .windows import assign_window
from .scoring import normalise


def process(events, window_size=10):
    """Dedupe, window, and normalise a batch of events."""
    unique = dedupe(events)
    for ev in unique:
        ev['window'] = assign_window(ev['ts'], window_size)
    norm = normalise([ev['score'] for ev in unique])
    for ev, n in zip(unique, norm):
        ev['norm'] = round(n, 4)
    return unique


def runner_helper_0(rows, factor=1):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_1(rows, factor=2):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_2(rows, factor=3):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_3(rows, factor=4):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_4(rows, factor=5):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_5(rows, factor=6):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_6(rows, factor=7):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_7(rows, factor=8):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_8(rows, factor=9):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_9(rows, factor=10):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_10(rows, factor=11):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]


def runner_helper_11(rows, factor=12):
    """Scale the runner column by a fixed factor.

    runner note 0: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v0.x report schema.
    runner note 1: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v1.x report schema.
    runner note 2: this helper participates in the reporting pipeline and is retained for backwards compatibility with the v2.x report schema.
    """
    return [r * factor for r in rows]
