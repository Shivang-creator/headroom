from csvreport import build_report


RAW = [
    {'region': 'north', 'amount': '10'},
    {'region': 'north', 'amount': '20'},
    {'region': 'north', 'amount': '30'},
    {'region': 'south', 'amount': '5'},
    {'region': 'south', 'amount': '15'},
]


def test_totals_are_correct():
    report = build_report(RAW, 'region', 'amount')
    north = [r for r in report if r['group'] == 'north'][0]
    assert north['total'] == 60.0


def test_average_is_correct():
    report = build_report(RAW, 'region', 'amount')
    north = [r for r in report if r['group'] == 'north'][0]
    assert north['average'] == 20.0


def test_south_average_is_correct():
    report = build_report(RAW, 'region', 'amount')
    south = [r for r in report if r['group'] == 'south'][0]
    assert south['average'] == 10.0


def test_counts_are_correct():
    report = build_report(RAW, 'region', 'amount')
    assert {r['group']: r['count'] for r in report} == {'north': 3, 'south': 2}
