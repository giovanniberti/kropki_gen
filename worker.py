import os
import re

import numpy as np
from celery import Celery

from generator import CellConstraint, grid_coords, DotType, DotConstraint
from model import generate_kropki_solution
from ken import constraints_to_grid
from ken import encode_constraints, retrieve_kropki_solution

import redis

from loguru import logger

app = Celery('worker', broker=os.getenv("REDIS_BROKER_URL"))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Setting up periodic generation task...")
    sender.add_periodic_task(120.0, worker_generate_kropki.s())


@app.task
def worker_generate_kropki():
    logger.info("Constructing new solution...")
    r = redis.from_url(os.getenv("REDIS_KEYS_URL"))
    store = [constraints_to_grid(decode_ken(str(s, 'utf8'))) for s in r.smembers("sudokus")]

    logger.info("Store has {} elements", len(store))
    solution = generate_kropki_solution(retrieve_kropki_solution(), store)

    constraints = set({CellConstraint(cell, solution[*cell]) for cell in grid_coords()})

    encoded_solution = encode_constraints(constraints)
    r.sadd("sudokus", encoded_solution)

    logger.info("Generated new sudoku: {}", encoded_solution)
