import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv("../backend/.env")

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME   = os.getenv("DB_NAME", "fitness_tracker")

client = MongoClient(MONGO_URL)
db     = client[DB_NAME]
col    = db["measurements"]

with open("measurements.json", encoding="utf-8") as f:
    records = json.load(f)

result = col.insert_many(records)
print(f"✅ {len(result.inserted_ids)} records inserted into MongoDB")