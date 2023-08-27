import os
import random
from itertools import product, chain

import redis
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



def generate_kropki_solution(store=None):
    if store is None:
        store = []

    model, solution = build_kropki_base_model()
    s = cp.SolverLookup.get("ortools", model)

    solution_found = s.solve()
    if solution_found and store:
        new_solution = solution.value()
        s.maximize(sum([np.sum(solution != sol) for sol in store]))
    elif solution_found and not store:
        new_solution = solution.value()
    elif not solution_found and store:
        new_solution = random.choice(store)
    else:
        raise RuntimeError("No solution found!")

    return new_solution
