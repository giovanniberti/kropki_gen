from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from generator import generate_kropki
from ken import encode_constraints, retrieve_kropki_solution
from worker import start_worker

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://kropki-gen.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
)


# start_worker()


@app.post("/kropki")
async def api_generate_kropki(sampling: int = 5):
    solution = retrieve_kropki_solution()
    kropki, full_solution = generate_kropki(solution, sampling)

    return {
        "ken": encode_constraints(kropki),
        "solution": encode_constraints(full_solution)
    }

