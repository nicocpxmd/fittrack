from fastapi import APIRouter, HTTPException
from app.database import measurements as col
from app.models import MeasurementRecord, MeasurementUpdate
from bson import ObjectId

router = APIRouter(prefix="/measurements", tags=["measurements"])

def serialize(doc) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("/", status_code=201)
async def create(record: MeasurementRecord):
    result = await col.insert_one(record.model_dump())
    return {"id": str(result.inserted_id)}

@router.get("/")
async def get_all():
    docs = await col.find().sort("date", 1).to_list(500)
    return [serialize(d) for d in docs]

@router.get("/{id}")
async def get_one(id: str):
    doc = await col.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(404, "Record not found")
    return serialize(doc)

@router.put("/{id}")
async def update(id: str, payload: MeasurementUpdate):
    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(400, "No update data provided")

    result = await col.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404, "Record not found")
    return {"updated": True}

@router.delete("/{id}", status_code=204)
async def delete(id: str):
    result = await col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Record not found")