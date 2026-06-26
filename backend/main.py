from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import db

app = FastAPI(title="Fitness Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Fitness Tracker API running"}



@app.get("/test-db")
async def test_db():
    collections = await db.list_collection_names()
    return {"status": "connected", "collections": collections}