from fastapi import APIRouter, HTTPException, Depends
from app.models import MeasurementRecord, MeasurementUpdate
from app.database import measurements
from app.auth import get_current_user_id
from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter()

@router.post("/", status_code=201)
async def create_measurement(
    record: MeasurementRecord,
    user_id: str = Depends(get_current_user_id)
):
    record_dict = record.model_dump()
    record_dict["date"] = record_dict["date"].isoformat()
    record_dict["user_id"] = user_id
    result = await measurements.insert_one(record_dict)
    return {"id": str(result.inserted_id)}

@router.get("/")
async def get_measurements(user_id: str = Depends(get_current_user_id)):
    cursor = measurements.find({"user_id": user_id}).sort("date", 1)
    results = await cursor.to_list(length=500)
    for doc in results:
        doc["id"] = str(doc.pop("_id"))
    return results

@router.get("/{id}")
async def get_measurement(id: str, user_id: str = Depends(get_current_user_id)):
    try:
        obj_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid id format")
    doc = await measurements.find_one({"_id": obj_id, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Record not found")
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.put("/{id}")
async def update_measurement(
    id: str,
    update_data: MeasurementUpdate,
    user_id: str = Depends(get_current_user_id)
):
    try:
        obj_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid id format")
    update_dict = update_data.get_dot_notation()
    if not update_dict:
        raise HTTPException(status_code=400, detail="No update data provided")
    result = await measurements.update_one(
        {"_id": obj_id, "user_id": user_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"updated": True}

@router.delete("/{id}", status_code=204)
async def delete_measurement(id: str, user_id: str = Depends(get_current_user_id)):
    try:
        obj_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid id format")
    result = await measurements.delete_one({"_id": obj_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return None
