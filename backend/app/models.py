from pydantic import BaseModel, Field
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
    weight_kg:    Optional[float] = Field(None, ge=20, le=300)
    height_cm:    Optional[float] = Field(None, ge=0)
    neck_cm:      Optional[float] = Field(None, ge=0)
    shoulder_cm:  Optional[float] = Field(None, ge=0)
    chest_cm:     Optional[float] = Field(None, ge=0)
    arm_cm:       Optional[float] = Field(None, ge=0)
    forearm_cm:   Optional[float] = Field(None, ge=0)
    waist_cm:     Optional[float] = Field(None, ge=0)
    abdomen_cm:   Optional[float] = Field(None, ge=0)
    hip_cm:       Optional[float] = Field(None, ge=0)
    upper_leg_cm: Optional[float] = Field(None, ge=0)
    lower_leg_cm: Optional[float] = Field(None, ge=0)
    calf_cm:      Optional[float] = Field(None, ge=0)

class MeasurementRecord(BaseModel):
    date:            str
    date_confidence: DateConfidence = DateConfidence.exact
    data_context:    DataContext    = DataContext.adult_baseline
    measurements:    Measurements
    notes:           Optional[str]  = ""

class MeasurementUpdate(BaseModel):
    measurements: Measurements