from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date as Date

class DateConfidence(str, Enum):
    exact      = "exact"
    month_only = "month_only"
    year_only  = "year_only"

class DataContext(str, Enum):
    adolescent_growth = "adolescent_growth"
    transition        = "transition"
    adult_baseline    = "adult_baseline"

class Measurements(BaseModel):
    # Field(gt=0) asegura que el valor sea mayor a 0
    weight_kg:    Optional[float] = Field(default=None, gt=0)
    height_cm:    Optional[float] = Field(default=None, gt=0)
    neck_cm:      Optional[float] = Field(default=None, gt=0)
    shoulder_cm:  Optional[float] = Field(default=None, gt=0)
    chest_cm:     Optional[float] = Field(default=None, gt=0)
    arm_cm:       Optional[float] = Field(default=None, gt=0)
    forearm_cm:   Optional[float] = Field(default=None, gt=0)
    waist_cm:     Optional[float] = Field(default=None, gt=0)
    abdomen_cm:   Optional[float] = Field(default=None, gt=0)
    hip_cm:       Optional[float] = Field(default=None, gt=0)
    upper_leg_cm: Optional[float] = Field(default=None, gt=0)
    lower_leg_cm: Optional[float] = Field(default=None, gt=0)
    calf_cm:      Optional[float] = Field(default=None, gt=0)

class MeasurementRecord(BaseModel):
    date:            Date  # Ahora exige formato YYYY-MM-DD
    date_confidence: DateConfidence = DateConfidence.exact
    data_context:    DataContext    = DataContext.adult_baseline
    measurements:    Measurements
    notes:           Optional[str]  = ""

class MeasurementUpdate(BaseModel):
    date:            Optional[Date]            = None
    date_confidence: Optional[DateConfidence]  = None
    data_context:    Optional[DataContext]     = None
    notes:           Optional[str]             = None
    measurements:    Optional[Measurements]    = None

    def get_dot_notation(self) -> dict:
        result = {}
        for field in ("date", "date_confidence", "data_context", "notes"):
            value = getattr(self, field)
            if value is not None:
                # Convertimos la fecha a string para MongoDB si existe
                if field == "date" and isinstance(value, Date):
                    result[field] = value.isoformat()
                else:
                    result[field] = value
        if self.measurements is not None:
            for k, v in self.measurements.model_dump().items():
                if v is not None:
                    result[f"measurements.{k}"] = v
        return result