from collections import defaultdict
from typing import Optional

from generator import Constraint, grid_coords, CellConstraint, DotConstraint, DotType

import redis
import os
import re
import numpy as np

def encode_dot_type(dot_type: Optional[DotType]):
    if dot_type == DotType.WHITE:
        return "w"
    elif dot_type == DotType.BLACK:
        return "k"
    else:
        return None


def encode_constraints_for_cell(constraints: set[Constraint]) -> str:
    value = None
    bottom = None
    right = None

    for constraint in constraints:
        if type(constraint) == CellConstraint:
            value = constraint.value
        elif type(constraint) == DotConstraint:
            reference_cell = constraint.reference_cell()
            other_cell = set(constraint.cells() - {constraint.reference_cell()}).pop()

            if reference_cell[0] == other_cell[0] and reference_cell[1] == other_cell[1] - 1:
                right = constraint.dot_type
            elif reference_cell[0] == other_cell[0] - 1 and reference_cell[1] == other_cell[1]:
                bottom = constraint.dot_type
            else:
                raise RuntimeError(f"Invalid cell combination for dot constraint! {constraint.cells()}")

            1 + 1

    if value is not None and bottom is None and right is None:
        return f"{value}"
    else:
        value = value or ""
        bottom = encode_dot_type(bottom) or "x"
        right = encode_dot_type(right) or "x"

        return f"({value}{bottom}{right})"


def rle_ken(ken: str) -> str:
    compact_ken = ""

    empty_cell_substitutions = {
        1: "A",
        2: "B",
        3: "C",
        4: "D",
        5: "E",
        6: "F",
        7: "G",
        8: "H"
    }

    a_count = 0
    for char in ken:
        if char == "A":
            a_count += 1
        else:
            if a_count > 0:
                compact_ken += empty_cell_substitutions[a_count]
                a_count = 0

            compact_ken += char

    return compact_ken


def encode_constraints(constraints_set: set[Constraint]) -> str:
    constraints_by_cell = defaultdict(set)

    for constraint in constraints_set:
        constraints_by_cell[constraint.reference_cell()].add(constraint)

    grid = list(sorted(grid_coords()))

    ken = ""
    for cell in grid:
        if cell in constraints_by_cell.keys():
            encoded = encode_constraints_for_cell(constraints_by_cell[cell])

            ken += encoded
        else:
            ken += "A"

        if cell[1] == 8 and cell[0] != 8:
            ken += "/"

    assert len(ken.split("/")) == 9, f"splits: {len(ken.split('/'))}"
    return rle_ken(ken)


def next_cell(cell):
    if cell[1] == 8 and cell[0] != 8:
        return cell[0] + 1, 0
    elif cell[1] == 8 and cell[0] == 8:
        return None
    else:
        return cell[0], cell[1] + 1

def letter_to_dot(letter):
    if letter == "w":
        return DotType.WHITE
    elif letter == "k":
        return DotType.BLACK
    else:
        return None

def decode_dot_constraints(constraint, cell):
    if len(constraint) == 4:
        par1, bottom, right, par2 = constraint.split("")
        value = None
    else:
        par1, value, bottom, right, par2 = constraint.split("")

    bottom = letter_to_dot(bottom)
    right = letter_to_dot(right)

    result = {}

    if bottom:
        result.add(DotConstraint({cell, (cell[0] + 1, cell[1])}))
    
    if right:
        result.add(DotConstraint({cell, (cell[0], cell[1] + 1)}))
    
    if value:
        result.add(CellConstraint(cell, int(value)))

    return result

def decode_value_constraint(constraint, cell):
    return CellConstraint(cell, int(constraint))

def decode_ken(ken):
    rows = ken.split("/")

    if len(rows) != 9:
        raise RuntimeError(f"Invalid number of rows! ({len(rows)} != 9)")
    
    constraints = set()
    cell = (0, 0)
    for r in rows:
        row = r
        while row:
            value_constraint = re.compile("[1-9]")
            dot_constraint = re.compile("\(([1-9])?(w|x|k)(w|x|k)\)")

            if value_constraint.match(row):
                constraint = row[0]
                row = row[1:]
                constraints.add(decode_value_constraint(constraint, cell))
                cell = next_cell(cell)
            elif dot_constraint.match(row):
                groups = dot_constraint.match(row).groups()
                if len(groups) == 2:
                    constraint = row[0:4]
                    row = row[5:]
                else:
                    constraint = row[0:5]
                    row = row[6:]

                constraints += decode_dot_constraints(constraint, cell)
                cell = next_cell(cell)

    return constraints

def constraints_to_grid(constraints):
    result = np.zeros(shape=(9, 9))

    for constraint in constraints:
        result[*constraint.reference_cell()] = constraint.value

    return result.astype(int)


def retrieve_kropki_solution():
    r = redis.from_url(os.getenv("REDIS_KEYS_URL"))

    return constraints_to_grid(decode_ken(str(r.srandmember("sudokus"), 'utf8')))
