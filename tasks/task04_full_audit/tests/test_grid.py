import pytest

from gridcalc import evaluate


def expected(row, col):
    return (row * 3) + (col * 1)


CASES = [(r, c) for r in range(22) for c in range(22)]


@pytest.mark.parametrize('row,col', CASES)
def test_every_cell_is_weighted_correctly(row, col):
    grid = evaluate(22, 22)
    context = {
        'row': row, 'col': col,
        'row_values': grid[row],
        'col_values': [grid[r][col] for r in range(22)],
    }
    assert grid[row][col] == expected(row, col), context
