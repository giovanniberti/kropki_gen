import random
from abc import ABC
from enum import Enum, auto
from functools import cache, total_ordering
from itertools import product, combinations
from typing import Iterable, Any

from cpmpy.expressions.core import Expression

from graph import a_star
from model import build_kropki_base_model, get_kropki_solution


@total_ordering
class Constraint(ABC):
    def __contains__(self, item):
        return item in self.cells()

    def __lt__(self, other):
        return isinstance(other, Constraint) and self.reference_cell() < other.reference_cell()

    def cells(self) -> frozenset[tuple[int, int]]:
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


def prefixed_sequence_generator(prefix: list[tuple[int, int]]):
    def sequence():
        grid = grid_coords() - set(prefix)

        for cell in prefix:
            yield cell

        while grid:
            yield grid.pop()

    return sequence


def get_last_chosen_cell_index(constraint_set: frozenset[Constraint], start_node: frozenset[Constraint]) -> int:
    chosen_cells, _ = partition_cells(constraint_set, start_node)
    return len(chosen_cells)


def partition_cells(constraint_set: frozenset[Constraint], start_node: frozenset[Constraint]) -> \
        tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    start_holes = grid_coords() - set(c.reference_cell() for c in start_node if type(c) is CellConstraint)
    sequence_generator = prefixed_sequence_generator(sorted(list(start_holes)))

    constrained_cells = {c.reference_cell(): c for c in constraint_set if type(c) is CellConstraint}
    holes = grid_coords() - constrained_cells.keys()

    last_chosen_cell = None
    chosen_cells = []
    possibly_chosen = []
    for c in sequence_generator():
        possibly_chosen.append(c)
        if c in holes:
            last_chosen_cell = c
            chosen_cells += possibly_chosen
            possibly_chosen = []
    candidate_cells = possibly_chosen

    if len(holes) > 0:
        assert chosen_cells[-1] == last_chosen_cell

    assert len(chosen_cells) + len(candidate_cells) == len(grid_coords())

    return chosen_cells, candidate_cells


def get_neighbor_constraints_set(constraint_set: frozenset[Constraint], start_node: frozenset[Constraint]) -> \
        frozenset[
            frozenset[Constraint]]:
    constrained_cells = {c.reference_cell(): c for c in constraint_set if type(c) is CellConstraint}
    _, candidate_cells = partition_cells(constraint_set, start_node)

    neighbor_constraint_sets = {constraint_set - {constrained_cells[c]} for c in candidate_cells}

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

            if dot_type == DotType.WHITE:
                return (grid[r1, c1] == grid[r2, c2] + 1) | (grid[r1, c1] + 1 == grid[r2, c2])
            elif dot_type == DotType.BLACK:
                return (grid[r1, c1] == grid[r2, c2] * 2) | (grid[r1, c1] * 2 == grid[r2, c2])
            else:
                raise ValueError("Unsupported dot type")

        return dot_constraint(grid, cell1, cell2, constraint.dot_type)
    else:
        raise ValueError("Invalid constraint type")


def is_minimal_constraint_set(constraints_set: set[Constraint]):
    # Check whether the constraint set is minimal, i.e. removing any further constraint
    # would allow multiple solutions

    value_constraints = set(filter(lambda c: type(c) is CellConstraint, constraints_set))

    for constraint in value_constraints:
        reduced_constraint_set = constraints_set - {constraint}
        number_of_solutions = get_number_of_solutions(reduced_constraint_set)

        assert number_of_solutions != 0

        if number_of_solutions == 1:
            return False

    return True


def get_number_of_solutions(constraints_set):
    base_model, grid = build_kropki_base_model()
    base_model += [constraint_to_model(grid, c) for c in constraints_set]
    number_of_solutions = base_model.solveAll(solution_limit=2)

    return number_of_solutions


def get_dot_constraints(solution):
    grid = grid_coords()

    dot_constraints = set()

    def is_dot(cell1, cell2):
        def is_black(cell1, cell2):
            return solution[*cell1].value() == solution[*cell2].value() * 2 or \
                   solution[*cell1].value() * 2 == solution[*cell2].value()

        def is_white(cell1, cell2):
            return solution[*cell1].value() == solution[*cell2].value() + 1 or \
                   solution[*cell1].value() + 1 == solution[*cell2].value()

        if is_black(cell1, cell2):
            return DotType.BLACK
        elif is_white(cell, cell2):
            return DotType.WHITE
        else:
            return None

    for cell in grid:
        r, c = cell
        right_cell = (r, c + 1)
        bottom_cell = (r + 1, c)

        if c != 8:
            right_dot = is_dot(cell, right_cell)

            if right_dot is not None:
                dot_constraints.add(DotConstraint({cell, right_cell}, right_dot))

        if r != 8:
            bottom_dot = is_dot(cell, bottom_cell)

            if bottom_dot is not None:
                dot_constraints.add(DotConstraint({cell, bottom_cell}, bottom_dot))

    return dot_constraints


def generate_kropki(sampled_constraints):
    solution = get_kropki_solution(5)

    value_constraints = {CellConstraint((r, c), solution[r, c].value()) for r, c in grid_coords()}
    dot_constraints = get_dot_constraints(solution)
    start_node = frozenset(value_constraints | dot_constraints)

    n = 0
    found = False
    for sampled_value_constraints in combinations(value_constraints, r=sampled_constraints):
        n += 1
        start_node = frozenset(set(sampled_value_constraints) | dot_constraints)

        if get_number_of_solutions(start_node) == 1:
            found = True
            break

    if not found:
        raise RuntimeError(f"Cannot find solution with {sampled_constraints} fixed constraints! "
                           f"Try to use a higher number instead. ({n} total combinations scanned)")

    def distance(i: frozenset[Constraint], j: frozenset[Constraint], start_node: frozenset[Constraint]):
        i_index = get_last_chosen_cell_index(i, start_node)
        j_index = get_last_chosen_cell_index(j, start_node)

        return abs(i_index - j_index)

    return a_star(
        start_node=start_node,
        is_goal=is_minimal_constraint_set,
        neighbors=lambda n: get_neighbor_constraints_set(n, start_node),
        h=lambda n: 0,
        d=lambda i, j: distance(i, j, start_node)
    ), value_constraints
