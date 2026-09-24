from fastapi import APIRouter, HTTPException
from app.database import measurements as col
from app.models import MeasurementRecord, MeasurementUpdate
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/measurements", tags=["measurements"])

def serialize(doc) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc

def parse_object_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except (InvalidId, TypeError):
        raise HTTPException(400, "Invalid id format")

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
    oid = parse_object_id(id)
    doc = await col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Record not found")
    return serialize(doc)

@router.put("/{id}")
async def update(id: str, payload: MeasurementUpdate):
    oid = parse_object_id(id)
    update_data = payload.get_dot_notation()
    if not update_data:
        raise HTTPException(400, "No update data provided")
    result = await col.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404, "Record not found")
    return {"updated": True}

@router.delete("/{id}", status_code=204)
async def delete(id: str):
    oid = parse_object_id(id)
    result = await col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(404, "Record not found")