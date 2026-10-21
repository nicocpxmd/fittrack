# services/users/app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#.env credentials
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL not configured on enviroment.")

#engine 
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=10, max_overflow=10, pool_timeout=10, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit =False, autoflush=False, bind=engine)

Base = declarative_base()

#db path inyection

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()