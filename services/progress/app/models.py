from pydantic import BaseModel, Field

class ProgressCalculateRequest(BaseModel):
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
