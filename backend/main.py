from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from bson import ObjectId
from app.database import measurements as collection

app = FastAPI(title="Fitness Tracker API")

from app.routers import measurements
app.include_router(measurements.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Fitness Tracker API running"}



@app.put("/measurements/{id}")
async def update_measurement(id: str, measurement: dict):
    result = await collection.update_one({"_id": ObjectId(id)}, {"$set": measurement})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"updated": True}