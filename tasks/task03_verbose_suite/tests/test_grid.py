import pytest

from gridcalc import evaluate


def expected(row, col):
    return (row * 3) + (col * 1)


CASES = [(r, c) for r in range(18) for c in range(18)]


@pytest.mark.parametrize('row,col', CASES)
def test_every_cell_is_weighted_correctly(row, col):
    grid = evaluate(18, 18)
    context = {
        'row': row, 'col': col,
        'row_values': grid[row],
        'col_values': [grid[r][col] for r in range(18)],
    }
    assert grid[row][col] == expected(row, col), context
