import random
from functools import cache
from itertools import product, chain

import cpmpy as cp
import numpy as np
from cpmpy.expressions.variables import NDVarArray


def build_kropki_base_model() -> tuple[cp.Model, NDVarArray]:
    grid = cp.intvar(1, 9, shape=(9, 9))

    all_different_in_row = (cp.AllDifferent(*(grid[r, i] for i in range(0, 9))) for r in range(0, 9))
    all_different_in_col = (cp.AllDifferent(*(grid[i, c] for i in range(0, 9))) for c in range(0, 9))

    cell_intervals = [list(range(0, 3)), list(range(3, 6)), list(range(6, 9))]
    all_different_in_cell = (cp.AllDifferent(grid[r, c] for r, c in product(*cell))
                             for cell in product(cell_intervals, cell_intervals))

    model = cp.Model()

    for c in chain(all_different_in_row, all_different_in_col, all_different_in_cell):
        model += c

    return model, grid


@cache
def generate_sudoku_solutions(maxsol=5):
    model, solution = build_kropki_base_model()
    s = cp.SolverLookup.get("ortools", model)

    store = []
    solutions = []
    while len(store) < maxsol and s.solve():
        store.append(solution.value())
        solutions.append(solution)
        s.maximize(sum([np.sum(solution != sol) for sol in store]))

    assert len(store) > 0
    return solutions


def get_kropki_solution(maxsol=5) -> NDVarArray:
    solutions = generate_sudoku_solutions(maxsol)

    return random.choice(solutions)
