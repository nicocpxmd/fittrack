import os
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

MEASUREMENTS_SERVICE_URL = os.getenv("MEASUREMENTS_SERVICE_URL", "http://192.168.100.3:8001")

async def fetch_measurements(token: str) -> list:
    base_url = MEASUREMENTS_SERVICE_URL.rstrip('/')
    url = f"{base_url}/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error communicating with measurements: {response.text}"
                )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Measurements error: {str(e)}"
            )
