import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncpg

app = FastAPI(title="PulseMatch Backend")

# Enable CORS so your Telegram Mini App frontend can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust or restrict to your frontend domain in production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch the database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
async def root():
    return {"status": "PulseMatch backend is online and connected!"}

@app.get("/profiles/{user_id}")
async def get_profiles(user_id: int):
    if not DATABASE_URL:
        raise HTTPException(
            status_code=500, 
            detail="DATABASE_URL environment variable is missing on the server."
        )
    
    try:
        # Connect asynchronously to your Supabase database using asyncpg
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch(
            """
            SELECT telegram_id, username, display_name, bio, location, photo 
            FROM users 
            WHERE telegram_id != $1
            """,
            user_id
        )
        await conn.close()
        
        # Convert asyncpg Record objects to standard dictionaries for JSON serialization
        return [dict(r) for r in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
