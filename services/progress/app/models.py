from pydantic import BaseModel, Field
from typing import Optional

class ProgressCalculateRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario en el servicio users")
    tipo_medida: str = Field(..., description="Clave de medida (ej. weight_kg)")
    desde: str = Field(..., description="Fecha inicial de filtrado (YYYY-MM-DD)")
    hasta: str = Field(..., description="Fecha final de filtrado (YYYY-MM-DD)")

class ProgressSnapshotResponse(BaseModel):
    id: str
    user_id: str
    tipo_medida: str
    valor_inicial: float
    valor_actual: float
    diferencia: float
    fecha_inicio: str
    fecha_fin: str
    created_at: str