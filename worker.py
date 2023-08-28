import os
import re
import traceback

import numpy as np

from time import sleep
from celery import Celery
from generator import CellConstraint, grid_coords, DotType, DotConstraint
from model import generate_kropki_solution
from ken import constraints_to_grid, decode_ken
from ken import encode_constraints, retrieve_kropki_solution

import redis

from loguru import logger

app = Celery('worker', broker=os.getenv("REDIS_BROKER_URL"))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Setting up periodic generation task...")
    worker_generate_kropki.delay()


@app.task
def worker_generate_kropki():
    try:
        worker_generate_kropki_impl()
    except Exception as e:
        logger.error("Exception while generating new solution: {}", e)
        traceback.print_exc()
    finally:
        worker_generate_kropki.delay()
        sleep(10)


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
