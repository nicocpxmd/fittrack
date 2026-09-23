# services/users/app/models.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.schemas import GenderEnum, FitnessGoalEnum, UnitsEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    fitness_goal: Optional[FitnessGoalEnum] = None
    preferred_units: UnitsEnum = UnitsEnum.metric

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    fitness_goal: Optional[FitnessGoalEnum] = None
    preferred_units: Optional[UnitsEnum] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    fitness_goal: Optional[FitnessGoalEnum] = None
    preferred_units: UnitsEnum
    created_at: datetime

    # This config tells Pydantic to read data even if it's not a standard dict (like a SQLAlchemy model)
    model_config = ConfigDict(from_attributes=True)

class PasswordRecovery(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str