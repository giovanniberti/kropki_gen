import os
import re
import traceback

import numpy as np

from multiprocessing import Process
from time import sleep
from generator import CellConstraint, grid_coords, DotType, DotConstraint
from model import generate_kropki_solution
from ken import constraints_to_grid, decode_ken
from ken import encode_constraints, retrieve_kropki_solution

import redis

from loguru import logger


def start_worker():
    p = Process(target=worker_generate_kropki)
    p.start()


def worker_generate_kropki():
    while True:
        try:
            worker_generate_kropki_impl()
        except Exception as e:
            logger.error("Exception while generating new solution: {}", e)
            traceback.print_exc()


def worker_generate_kropki_impl():
    logger.info("Constructing new solution...")
    r = redis.from_url(os.getenv("REDIS_KEYS_URL"))
    sudokus = r.smembers("sudokus")
    store = [constraints_to_grid(decode_ken(str(s, 'utf8'))) for s in sudokus]

    logger.info("Store has {} elements", len(store))
    solution = generate_kropki_solution(store)

    constraints = set({CellConstraint(cell, solution[*cell]) for cell in grid_coords()})

    encoded_solution = encode_constraints(constraints)
    r.sadd("sudokus", encoded_solution)

    logger.info("Generated new sudoku: {}", encoded_solution)


if __name__ == "__main__":
    start_worker()

