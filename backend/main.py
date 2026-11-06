from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PulseMatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "healthy", "app": "PulseMatch API"}

@app.get("/match/next")
def get_next_match():
    return {"id": 1, "username": "TestProfile", "bio": "Looking for connection!"}
