from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import List
from app.models import ProgressCalculateRequest, ProgressSnapshotResponse
from app.database import progress_collection
from app.clients import fetch_measurements, validate_user

router = APIRouter(prefix="/progress", tags=["progress"])
security = HTTPBearer()

@router.post("/calculate", response_model=ProgressSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def calculate_progress(
    payload: ProgressCalculateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # 1. Validar el token contra el servicio users
    await validate_user(token)

    # 2. Consultar mediciones del servicio measurements enviando únicamente el token
    raw_measurements = await fetch_measurements(token)

    # 3. Filtrar por rango de fechas y tipo_medida analizando el diccionario anidado
    filtered = []
    for record in raw_measurements:
        rec_date = record.get("date")
        measurements_dict = record.get("measurements", {})

        if rec_date and payload.desde <= rec_date <= payload.hasta:
            val = measurements_dict.get(payload.tipo_medida)
            if val is not None:
                filtered.append({
                    "date": rec_date,
                    "value": float(val)
                })

    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No measurements found for type '{payload.tipo_medida}' in the specified range."
        )

    # 4. Ordenar cronológicamente para extraer valor inicial y actual
    filtered.sort(key=lambda x: x["date"])

    valor_inicial = filtered[0]["value"]
    fecha_inicio = filtered[0]["date"]

    valor_actual = filtered[-1]["value"]
    fecha_fin = filtered[-1]["date"]

    diferencia = round(valor_actual - valor_inicial, 4)
    created_at = datetime.utcnow().isoformat()

    # 5. Construir y guardar el snapshot en MongoDB
    doc = {
        "user_id": payload.user_id,
        "tipo_medida": payload.tipo_medida,
        "valor_inicial": valor_inicial,
        "valor_actual": valor_actual,
        "diferencia": diferencia,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "created_at": created_at
    }

    result = await progress_collection.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/{user_id}", response_model=List[ProgressSnapshotResponse])
async def get_user_progress(user_id: str):
    cursor = progress_collection.find({"user_id": user_id})
    snapshots = []
    async for document in cursor:
        document["id"] = str(document["_id"])
        snapshots.append(document)
    return snapshots
