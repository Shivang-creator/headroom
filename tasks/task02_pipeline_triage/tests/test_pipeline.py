from evpipe import process


EVENTS = [
    {'id': 'a', 'ts': 10, 'score': 20, 'tag': 'first-a'},
    {'id': 'b', 'ts': 11, 'score': 40, 'tag': 'first-b'},
    {'id': 'a', 'ts': 12, 'score': 99, 'tag': 'second-a'},
    {'id': 'c', 'ts': 20, 'score': 60, 'tag': 'first-c'},
]


def test_dedupe_keeps_first_occurrence():
    out = process(EVENTS)
    tags = {e['id']: e['tag'] for e in out}
    assert tags == {'a': 'first-a', 'b': 'first-b', 'c': 'first-c'}


def test_window_boundaries_are_inclusive_at_start():
    out = process(EVENTS)
    windows = {e['id']: e['window'] for e in out}
    assert windows == {'a': 1, 'b': 1, 'c': 2}


def test_scores_are_min_max_normalised():
    out = process(EVENTS)
    norms = {e['id']: e['norm'] for e in out}
    assert norms == {'a': 0.0, 'b': 0.5, 'c': 1.0}
