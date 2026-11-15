"""Autorizacion de la API de analitica: solo usuarios con rol admin.

La validacion del token se delega al servicio de usuarios (/users/me), que es el
mismo patron que ya usan measurements y progress. Asi el rol siempre esta fresco:
si un administrador deja de serlo, pierde el acceso en la siguiente peticion.
"""
import os

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users:8002").rstrip("/")
USERS_TIMEOUT = float(os.getenv("USERS_TIMEOUT_SECONDS", "3"))

security = HTTPBearer(auto_error=False)


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Devuelve el perfil del usuario si es admin; si no, corta con 401/403/503."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        response = requests.get(
            f"{USERS_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {credentials.credentials}"},
            timeout=USERS_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo validar el token con el servicio de usuarios.",
        ) from exc

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas o token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de usuarios respondio de forma inesperada.",
        )

    try:
        perfil = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Respuesta invalida del servicio de usuarios.",
        ) from exc

    if perfil.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador para ver la analitica.",
        )

    return perfil
