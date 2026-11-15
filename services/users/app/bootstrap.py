"""Crea o promueve el usuario administrador al arrancar el servicio.

Se activa solo si existen ADMIN_EMAIL y ADMIN_PASSWORD en el entorno. Es idempotente:
si el usuario ya existe no le toca la contrasena, y si existe como usuario normal lo
promueve a administrador.
"""
import logging
import os

from pydantic import EmailStr, TypeAdapter
from sqlalchemy.exc import IntegrityError

from app import schemas
from app.database import SessionLocal
from app.security import get_password_hash

logger = logging.getLogger("bootstrap")

_email_adapter = TypeAdapter(EmailStr)


def asegurar_admin() -> None:
    email_raw = (os.getenv("ADMIN_EMAIL") or "").strip()
    password = os.getenv("ADMIN_PASSWORD") or ""
    full_name = (os.getenv("ADMIN_FULL_NAME") or "Administrador").strip()

    if not email_raw or not password:
        logger.info(
            "ADMIN_EMAIL y ADMIN_PASSWORD no configurados: no se crea administrador."
        )
        return

    if password == "changeme":
        logger.warning(
            "ADMIN_PASSWORD sigue con el valor de ejemplo ('changeme'). "
            "Cambialo antes de exponer el servicio."
        )

    try:
        email = str(_email_adapter.validate_python(email_raw))
    except Exception as exc:  # email invalido: se avisa y no se bloquea el arranque
        logger.error("ADMIN_EMAIL no es un correo valido (%s): %s", email_raw, exc)
        return

    db = SessionLocal()
    try:
        user = db.query(schemas.User).filter(schemas.User.email == email).first()

        if user is None:
            try:
                db.add(
                    schemas.User(
                        email=email,
                        password_hash=get_password_hash(password),
                        full_name=full_name,
                        role="admin",
                    )
                )
                db.commit()
                logger.info("Administrador creado: %s", email)
            except IntegrityError:
                # Con varias replicas pueden intentar crearlo a la vez.
                db.rollback()
                logger.info(
                    "El administrador %s ya existia (creado por otra replica).", email
                )
            return

        if user.role != "admin":
            user.role = "admin"
            db.commit()
            logger.info("Usuario existente promovido a administrador: %s", email)
            return

        logger.info("El administrador %s ya existe.", email)
    except Exception:
        # Nunca se cae el servicio por el bootstrap: se registra y se sigue.
        db.rollback()
        logger.exception("No se pudo preparar el administrador.")
    finally:
        db.close()
