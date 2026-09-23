#services/users/main.py
import time
import logging
from fastapi import FastAPI, Request
from app.routers import users
from app.database import engine
from app import schemas

#logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logger")

#app
app = FastAPI(title= "FitTrack - Users API")
schemas.Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} {response.status_code} - {process_time}"
    )
    return response

app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
async def root():
    return {"message": "Users service is running"}