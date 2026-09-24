import os
import httpx
from fastapi import HTTPException, status, Header
from dotenv import load_dotenv

load_dotenv()

MEASUREMENTS_SERVICE_URL = os.getenv("MEASUREMENTS_SERVICE_URL", "http://localhost:8001")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8002")

async def fetch_measurements() -> list:
    """Obtiene todos los registros del microservicio measurements."""
    url = f"{MEASUREMENTS_SERVICE_URL.rstrip('/')}/measurements/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Error communicating with measurements service"
                )
            return response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Measurements service is unreachable"
            )

async def validate_user(authorization: str = None):
    """
    Valida el usuario autenticado consultando el endpoint GET /users/me 
    del microservicio users.
    """
    if not authorization:
        # Si no se envía el header, dejamos pasar o simulamos según prefieras en desarrollo local.
        return
    
    url = f"{USERS_SERVICE_URL.rstrip('/')}/users/me"
    headers = {"Authorization": authorization}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=3.0)
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
        except httpx.RequestError:
            # TODO: Modo sin validar / fallback por si el servicio users aún no está levantado en local.
            pass