from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import progress

app = FastAPI(
    title="FitTrack Progress Service",
    version="1.0.0",
    description="Microservicio de cálculo y almacenamiento de snapshots de progreso."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(progress.router)

@app.get("/")
def root():
    return {"service": "progress", "status": "running"}