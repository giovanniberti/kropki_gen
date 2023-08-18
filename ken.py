from collections import defaultdict

from generator import Constraint, grid_coords, CellConstraint, DotConstraint


def encode_constraints_for_cell(constraints: set[Constraint]) -> str:
    value = None
    bottom = None
    right = None

    for constraint in constraints:
        if type(constraint) == CellConstraint:
            value = constraint.value
        elif type(constraint) == DotConstraint:
            cells = constraint.cells()
            if cells[0][0] == cells[1][0] and cells[0][1] == cells[1][1] - 1:
                right = constraint.dot_kind
            elif cells[0][0] == cells[1][0] - 1 and cells[0][1] == cells[1][1]:
                bottom = constraint.dot_kind
            else:
                raise RuntimeError(f"Invalid cell combination for dot constraint! {constraint.cells()}")

    if value is not None and bottom is None and right is None:
        return f"{value}"
    else:
        value = value or ""
        bottom = bottom or "x"
        right = right or "x"

        return f"({value}{bottom}{right})"


def encode_constraints(constraints_set: set[Constraint]) -> str:
    constraints_by_cell = defaultdict(set)

    for constraint in constraints_set:
        constraints_by_cell[constraint.reference_cell()].add(constraint)

    grid = grid_coords()

    ken = ""
    for cell in grid:
        if cell in constraints_by_cell.keys():
            ken += encode_constraints_for_cell(constraints_by_cell[cell])
        else:
            ken += "A"

        if cell[1] == 8 and cell[0] != 8:
            ken += "/"

    return ken
