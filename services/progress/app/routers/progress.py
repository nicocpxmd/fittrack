from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from typing import List
from app.models import ProgressCalculateRequest, ProgressSnapshotResponse
from app.database import progress_collection
from app.clients import fetch_measurements
from app.auth import verify_user
from bson import ObjectId
from pymongo import ReturnDocument

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/calculate", response_model=ProgressSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def calculate_progress(
    payload: ProgressCalculateRequest,
    current_user: dict = Depends(verify_user)
):
    raw_measurements = await fetch_measurements(current_user["token"])

    filtered = []
    for record in raw_measurements:
        rec_date = record.get("date")
        measurements_dict = record.get("measurements", {})
        if rec_date and payload.desde <= rec_date <= payload.hasta:
            val = measurements_dict.get(payload.tipo_medida)
            if val is not None:
                filtered.append({"date": rec_date, "value": float(val)})

    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No measurements found for type '{payload.tipo_medida}' in the specified range."
        )

    filtered.sort(key=lambda x: x["date"])
    valor_inicial = filtered[0]["value"]
    fecha_inicio = filtered[0]["date"]
    valor_actual = filtered[-1]["value"]
    fecha_fin = filtered[-1]["date"]
    diferencia = round(valor_actual - valor_inicial, 4)
    created_at = datetime.utcnow().isoformat()

    doc = {
        "user_id": current_user["id"],
        "tipo_medida": payload.tipo_medida,
        "valor_inicial": valor_inicial,
        "valor_actual": valor_actual,
        "diferencia": diferencia,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "created_at": created_at
    }
    saved = await progress_collection.find_one_and_update(
        {
            "user_id": doc["user_id"],
            "tipo_medida": doc["tipo_medida"],
            "fecha_inicio": doc["fecha_inicio"],
            "fecha_fin": doc["fecha_fin"],
        },
        {
            "$set": {
                "valor_inicial": doc["valor_inicial"],
                "valor_actual": doc["valor_actual"],
                "diferencia": doc["diferencia"],
            },
            "$setOnInsert": {"created_at": doc["created_at"]},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    saved["id"] = str(saved["_id"])
    return saved

@router.get("/me", response_model=List[ProgressSnapshotResponse])
async def get_my_progress(current_user: dict = Depends(verify_user)):
    cursor = progress_collection.find({"user_id": current_user["id"]})
    snapshots = []
    async for document in cursor:
        document["id"] = str(document["_id"])
        snapshots.append(document)
    return snapshots


@router.delete("/{snapshot_id}")
async def delete_progress(snapshot_id: str, current_user: dict = Depends(verify_user)):
    if not ObjectId.is_valid(snapshot_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    result = await progress_collection.delete_one(
        {"_id": ObjectId(snapshot_id), "user_id": current_user["id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return {"message": "Progreso eliminado"}
