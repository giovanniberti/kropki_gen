from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from generator import generate_kropki
from ken import encode_constraints
from model import generate_sudoku_solutions

app = FastAPI()

logger.info("Generating initial sudoku solutions...")
max_generatable_solutions = 50
generate_sudoku_solutions(max_generatable_solutions)
logger.info("Generating initial sudoku solutions... Done")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
)

@app.post("/kropki")
async def api_generate_kropki(sampling: int = 5):
    kropki, full_solution = generate_kropki(sampling)

    return {
        "ken": encode_constraints(kropki),
        "solution": encode_constraints(full_solution)
    }
