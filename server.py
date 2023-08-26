from fastapi import FastAPI

from generator import generate_kropki
from ken import encode_constraints

app = FastAPI()


@app.post("/kropki")
async def api_generate_kropki(sampling: int = 5):
    kropki, full_solution = generate_kropki(sampling)

    return {
        "ken": encode_constraints(kropki),
        "solution": encode_constraints(full_solution)
    }
