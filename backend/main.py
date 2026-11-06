import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg

app = FastAPI(title="PulseMatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

class UserCreate(BaseModel):
    telegram_id: int
    username: str
    bio: str = None

class SwipeCreate(BaseModel):
    user_id: int
    target_id: int
    action: str

@app.get("/")
def read_root():
    return {"status": "healthy", "app": "PulseMatch API"}

@app.post("/users")
async def register_user(user: UserCreate):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(
            """
            INSERT INTO users (telegram_id, username, bio) 
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET username = EXCLUDED.username, bio = EXCLUDED.bio;
            """,
            user.telegram_id, user.username, user.bio
        )
        await conn.close()
        return {"status": "success", "message": "User registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/match/next")
async def get_next_match():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        row = await conn.fetchrow("SELECT telegram_id as id, username, bio FROM users ORDER BY RANDOM() LIMIT 1")
        await conn.close()
        if row:
            return dict(row)
        return {"id": 0, "username": "No Profiles", "bio": "Check back later!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swipe")
async def record_swipe(swipe: SwipeCreate):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(
            "INSERT INTO swipes (user_id, target_id, action) VALUES ($1, $2, $3)",
            swipe.user_id, swipe.target_id, swipe.action
        )
        await conn.close()
        return {"status": "recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        @app.get("/profiles/{user_id}")
async def get_profiles(user_id: int):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # Fetch profiles excluding the current user
        rows = await conn.fetch(
            """
            SELECT telegram_id, username, display_name, bio, location, photo 
            FROM users 
            WHERE telegram_id != $1
            """,
            user_id
        )
        await conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

