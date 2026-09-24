from pydantic import BaseModel
from typing import Optional
from enum import Enum

class DateConfidence(str, Enum):
    exact      = "exact"
    month_only = "month_only"
    year_only  = "year_only"

class DataContext(str, Enum):
    adolescent_growth = "adolescent_growth"
    transition        = "transition"
    adult_baseline    = "adult_baseline"

class Measurements(BaseModel):
    weight_kg:    Optional[float] = None
    height_cm:    Optional[float] = None
    neck_cm:      Optional[float] = None
    shoulder_cm:  Optional[float] = None
    chest_cm:     Optional[float] = None
    arm_cm:       Optional[float] = None
    forearm_cm:   Optional[float] = None
    waist_cm:     Optional[float] = None
    abdomen_cm:   Optional[float] = None
    hip_cm:       Optional[float] = None
    upper_leg_cm: Optional[float] = None
    lower_leg_cm: Optional[float] = None
    calf_cm:      Optional[float] = None

class MeasurementRecord(BaseModel):
    date:            str
    date_confidence: DateConfidence = DateConfidence.exact
    data_context:    DataContext    = DataContext.adult_baseline
    measurements:    Measurements
    notes:           Optional[str]  = ""

class MeasurementUpdate(BaseModel):
    date:            Optional[str]            = None
    date_confidence: Optional[DateConfidence]  = None
    data_context:    Optional[DataContext]     = None
    notes:           Optional[str]             = None
    measurements:    Optional[Measurements]    = None

    def get_dot_notation(self) -> dict:
        result = {}
        for field in ("date", "date_confidence", "data_context", "notes"):
            value = getattr(self, field)
            if value is not None:
                result[field] = value
        if self.measurements is not None:
            for k, v in self.measurements.model_dump().items():
                if v is not None:
                    result[f"measurements.{k}"] = v
        return result