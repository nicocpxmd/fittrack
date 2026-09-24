import uuid
import enum
from sqlalchemy import Column, String, Date, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base

# SQLAlchemy enums
class GenderEnum(str, enum.Enum):
    M = "M"
    F = "F"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"

class FitnessGoalEnum(str, enum.Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    maintenance = "maintenance"
    endurance = "endurance"

class UnitsEnum(str, enum.Enum):
    metric = "metric"
    imperial = "imperial"

class User(Base):
    __tablename__ = "users"

    # UUID strings for pk
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SQLEnum(GenderEnum, name="gender_enum"), nullable=True)
    fitness_goal = Column(SQLEnum(FitnessGoalEnum, name="fitness_goal_enum"), nullable=True)
    preferred_units = Column(SQLEnum(UnitsEnum, name="units_enum"), default=UnitsEnum.metric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())