from abc import ABC
from enum import Enum, auto
from itertools import product
from typing import Iterable, Any

from cpmpy.expressions.core import Expression

from graph import a_star
from model import build_kropki_base_model


class Constraint(ABC):
    def __contains__(self, item):
        return item in self.cells()

    def cells(self) -> set[tuple[int, int]]:
        raise NotImplementedError()

    def reference_cell(self) -> tuple[int, int]:
        raise NotImplementedError()


class CellConstraint(Constraint):
    def __init__(self, cell, value):
        self.cell = cell
        self.value = value

    def cells(self) -> frozenset[tuple[int, int]]:
        return frozenset({self.cell})

    def reference_cell(self) -> tuple[int, int]:
        return self.cell

    def __eq__(self, o) -> bool:
        return self.value == o.value and self.cell == o.cell

    def __hash__(self) -> int:
        return hash(repr(self))

    def __contains__(self, item):
        return item == self.cell

    def __str__(self):
        return f"CellConstraint(cell={self.cell}, value={self.value})"

    def __repr__(self):
        return f"CellConstraint(cell={self.cell}, value={self.value})"


class DotType(Enum):
    BLACK = auto()
    WHITE = auto()


class DotConstraint(Constraint):
    def __init__(self, cells: set[tuple[int, int]], dot_type: DotType):
        assert len(cells) == 2

        self._cells = frozenset(cells)
        self.dot_type = dot_type

    def cells(self) -> frozenset[tuple[int, int]]:
        return self._cells

    def reference_cell(self) -> tuple[int, int]:
        return min(self._cells)

    def __eq__(self, o) -> bool:
        return self.dot_type == o.dot_type and self._cells == o._cells

    def __hash__(self) -> int:
        return hash(repr(self))

    def __str__(self):
        return f"DotConstraint(cells={self._cells}, type={self.dot_type})"

    def __repr__(self):
        return f"DotConstraint(cells={self._cells}, type={self.dot_type})"


def grid_coords(dim=9) -> set[tuple[Any, Any]]:
    return set(product(range(0, dim), range(0, dim)))


def get_constrained_cells(constraint_set: Iterable[Constraint]):
    constrained_cells = {cell for constraint in constraint_set for cell in constraint.cells()}

    return constrained_cells


def get_neighbor_constraints_set(constraint_set: frozenset[Constraint], base_solution) -> frozenset[
    frozenset[Constraint]]:
    neighbor_constraint_sets = set()
    grid = grid_coords()

    for cell in grid:
        new_constraint = CellConstraint(cell, base_solution[*cell].value())
        if new_constraint not in constraint_set:
            neighbor_constraint_sets.add(frozenset(constraint_set | {new_constraint}))

    return frozenset(neighbor_constraint_sets)


def constraint_to_model(grid, constraint: Constraint) -> Expression:
    if type(constraint) is CellConstraint:
        r, c = set(constraint.cells()).pop()
        return grid[r, c] == constraint.value
    elif type(constraint) is DotConstraint:
        cells = set(constraint.cells()).copy()
        cell1 = cells.pop()
        cell2 = cells.pop()

        def dot_constraint(grid, cell1, cell2, dot_type):
            r1, c1 = cell1
            r2, c2 = cell2

            if dot_type == DotType.BLACK:
                return (grid[r1, c1] == grid[r2, c2] + 1) | (grid[r1, c1] + 1 == grid[r2, c2])
            elif dot_type == DotType.WHITE:
                return (grid[r1, c1] == grid[r2, c2] * 2) | (grid[r1, c1] * 2 == grid[r2, c2])
            else:
                raise ValueError("Unsupported dot type")

        return dot_constraint(grid, cell1, cell2, constraint.dot_type)
    else:
        raise ValueError("Invalid constraint type")


def is_minimal_constraint_set(constraints_set: set[Constraint]):
    number_of_solutions = get_number_of_solutions(constraints_set)

    return number_of_solutions == 1


def get_number_of_solutions(constraints_set):
    base_model, grid = build_kropki_base_model()
    base_model += [constraint_to_model(grid, c) for c in constraints_set]
    number_of_solutions = base_model.solveAll(solution_limit=2)

    return number_of_solutions


def generate_kropki():
    model, solution = build_kropki_base_model()
    model.solve()

    start_node = frozenset({})

    def distance(i: frozenset[Constraint], j: frozenset[Constraint]):
        return len(i.symmetric_difference(j))

    return a_star(
        start_node=start_node,
        is_goal=is_minimal_constraint_set,
        neighbors=lambda n: get_neighbor_constraints_set(n, solution),
        h=lambda n: 0,
        d=distance
    )
