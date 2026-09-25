import os
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

MEASUREMENTS_SERVICE_URL = os.getenv("MEASUREMENTS_SERVICE_URL", "http://localhost:8001")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8002")

async def fetch_measurements(token: str) -> list:
    # Apuntamos a la raíz del servicio measurements porque no tiene el prefijo /measurements
    base_url = MEASUREMENTS_SERVICE_URL.rstrip('/')
    url = f"{base_url}/"

    auth_header = f"Bearer {token}" if not token.startswith("Bearer ") else token
    headers = {"Authorization": auth_header}

    print(f"PROGRESS CLIENT DEBUG - URL corregida: {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=5.0)
            print(f"PROGRESS CLIENT DEBUG - Status: {response.status_code}, Body: {response.text}")

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error communicating with measurements: {response.text}"
                )
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Measurements error: {str(e)}"
            )

async def validate_user(token: str):
    url = f"{USERS_SERVICE_URL.rstrip('/')}/users/me"
    auth_header = f"Bearer {token}" if not token.startswith("Bearer ") else token
    headers = {"Authorization": auth_header}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=3.0)
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
        except httpx.RequestError:
            pass
