from collections import defaultdict
from typing import Optional

from generator import Constraint, CellConstraint, DotConstraint, DotType


def compare_constraints(c1: Constraint, c2: Constraint):
    cells_c1 = list(c1.cells()).sort()
    cells_c2 = list(c2.cells()).sort()

    return (cells_c1 > cells_c2) - (cells_c1 < cells_c2)


def encode_dot_type(t: Optional[DotType]):
    if t is None:
        return "x"
    elif t == DotType.WHITE:
        return "w"
    elif t == DotType.BLACK:
        return "k"
    else:
        raise ValueError("Invalid DotType!")


def encode_cell(c: set[Constraint]):
    assert len(c) <= 3

    value = None
    bottom_dot = None
    right_dot = None

    for constraint in c:
        if type(constraint) is CellConstraint:
            value = constraint.value
        elif type(constraint) is DotConstraint:
            # Invariant: first cell (current cell) is top or left wrt to the second

            cell1, cell2 = list(constraint.cells())

            if cell1[1] == cell2[1] - 1:
                # first cell is left of second
                right_dot = constraint.dot_type

            elif cell1[0] == cell2[0] - 1:
                # first cell is top of second
                bottom_dot = constraint.dot_type

    encoded_value = str(value) if value else ""

    if bottom_dot is None and right_dot is None:
        return str(value)
    else:
        return f"({encoded_value}{encode_dot_type(bottom_dot)}{encode_dot_type(right_dot)})"


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def generate_board_code(constraint_set: set[Constraint]):
    grid = [(r, c) for r in range(0, 9) for c in range(0, 9)]

    constraints_by_cell = defaultdict(set)
    for constraint in constraint_set:
        cells: list[tuple[int, int]] = list(constraint.cells())
        cells.sort()

        if cells:
            constraints_by_cell[cells[0]].add(constraint)

    encoded = ""
    for row in chunks(grid, 8):
        for cell in row:
            encoded += encode_cell(constraints_by_cell[cell])

        encoded += "/"

    return encoded
