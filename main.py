from itertools import product

import cpmpy as cp


def main():
    grid = cp.intvar(1, 9, shape=(9, 9))

    all_different_in_row = (cp.AllDifferent(*(grid[r, i] for i in range(0, 9))) for r in range(0, 9))
    all_different_in_col = (cp.AllDifferent(*(grid[i, c] for i in range(0, 9))) for c in range(0, 9))

    cell_intervals = [list(range(0, 3)), list(range(3, 6)), list(range(6, 9))]
    all_different_in_cell = (cp.AllDifferent(grid[r, c] for r, c in product(*cell))
                             for cell in product(cell_intervals, cell_intervals))

    m = cp.Model(
        *all_different_in_row,
        *all_different_in_col,
        *all_different_in_cell,
    )

    solution_found = m.solve()

    if solution_found:
        print(grid.value())
    else:
        print("No solution")


if __name__ == '__main__':
    main()
