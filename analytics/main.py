"""API de solo lectura para los KPIs que produce Spark.

Lee /data/analytics.json (montado desde /root/fittrack/analytics/data) y lo
sirve por secciones. No habla con Spark ni con las bases de datos: el batch ya
dejo los resultados calculados.
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DATA_FILE = Path(os.environ.get("DATA_FILE", "/data/analytics.json"))

app = FastAPI(title="FitTrack - Analytics API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_cache = {"mtime": None, "data": None}


def load_data():
    """Carga el JSON y lo cachea hasta que cambie el archivo."""
    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail=f"No existe {DATA_FILE}. Ejecuta spark/run_all.sh primero.",
        )
    mtime = DATA_FILE.stat().st_mtime
    if _cache["mtime"] != mtime:
        with DATA_FILE.open(encoding="utf-8") as handle:
            _cache["data"] = json.load(handle)
        _cache["mtime"] = mtime
    return _cache["data"]


@app.get("/health")
def health():
    data = load_data()
    return {
        "status": "ok",
        "generated_at": data.get("generated_at"),
        "users": data.get("dataset", {}).get("usuarios"),
    }


@app.get("/dashboard")
def dashboard():
    """Todo lo que necesita la pestaña Analitica en una sola peticion."""
    return load_data()


@app.get("/kpis")
def kpis():
    return load_data().get("kpis", {})


@app.get("/summary")
def summary():
    data = load_data()
    return {
        "dataset": data.get("dataset", {}),
        "limpieza": data.get("limpieza", {}),
        "kpis": data.get("kpis", {}),
    }


@app.get("/retention")
def retention():
    return load_data().get("retencion", {})


@app.get("/adherence")
def adherence():
    return load_data().get("adherencia", [])


@app.get("/goals")
def goals():
    return load_data().get("metas", {})


@app.get("/weight")
def weight():
    return load_data().get("peso", {})


@app.get("/routines")
def routines():
    return load_data().get("rutinas", {})


@app.get("/seasonality")
def seasonality():
    return load_data().get("estacionalidad", {})


@app.get("/cities")
def cities():
    return load_data().get("ciudades", [])


@app.get("/validation")
def validation():
    return load_data().get("validacion", {})
