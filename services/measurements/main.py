from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fitness Tracker API")

from app.routers import measurements
app.include_router(measurements.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.100.2:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Fitness Tracker API running"}
