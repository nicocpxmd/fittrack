from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "fitness_tracker")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

measurements = db["measurements"]
