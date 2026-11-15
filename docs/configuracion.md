# Configuración: variables, puertos y roles

[<- Volver al README](../README.md)

## Variables del stack

| Variable | Uso |
|---|---|
| `POSTGRES_PASSWORD` | contraseña de Postgres (users) |
| `DB_PASSWORD` | contraseña root de MySQL (workouts, goals) |
| `SECRET_KEY` | firma de los JWT |
| `ADMIN_EMAIL` | correo del administrador que verá la analítica |
| `ADMIN_PASSWORD` | contraseña de ese administrador |
| `ADMIN_FULL_NAME` | nombre visible del administrador (opcional) |
| `FITTRACK_DIR` | ruta del repo en el nodo server (solo Swarm) |

`.env` no se versiona. `.env.example` tiene valores de ejemplo.

## Puertos

| Puerto | Servicio |
|---|---|
| `8080` | HAProxy / dashboard |
| `8404` | stats de HAProxy |
| `5432`, `27017`, `3306` | bases de datos (solo red interna) |
| `8001`–`8006` | servicios (solo red interna) |

## Variables de Spark

| Variable | Por defecto | Uso |
|---|---|---|
| `SPARK_HOME` | — | ruta de Spark si no está en `PATH` |
| `SPARK_SUBMIT` | `spark-submit` | binario explícito |
| `MASTER` | `local[*]` | `local[4]` o `spark://<server>:7077` |
| `ROOT` | raíz del repo | ruta del proyecto |
| `DRIVER_MEMORY` | `768m` | memoria del driver |
| `EXECUTOR_MEMORY` | `1500m` | memoria del executor (modo clúster) |

Los scripts `spark/run_*.sh` detectan la raíz del repo automáticamente y aceptan estas variables.

## Roles y acceso

Hay dos roles: `user` y `admin`. El registro público siempre crea `user`; el rol nunca se acepta desde
el cliente.

El administrador se define por configuración y se crea (o se promueve) al arrancar el servicio:

```bash
ADMIN_EMAIL=admin@tudominio.com
ADMIN_PASSWORD=<una contraseña nueva>
```

- Si el correo no existe, se crea con rol `admin` y esa contraseña.
- Si ya existe como `user`, se promueve a `admin` **sin cambiarle la contraseña**.
- Si no defines las variables, no se crea ningún administrador.

Cambiar `ADMIN_PASSWORD` después **no** actualiza una cuenta ya creada: usa el flujo de recuperación o
cámbiala en la base.

**Bases creadas antes de existir el rol.** `create_all` no agrega columnas a una tabla existente.
Aplica la migración (es idempotente):

```bash
# Compose
docker compose exec -T postgres psql -U fittrack -d fittrack_users \
  < docker/migrations/001_add_role.sql

# Swarm
docker exec -i $(docker ps -qf name=fittrack_postgres) psql -U fittrack -d fittrack_users \
  < docker/migrations/001_add_role.sql
```

Después reinicia el servicio `users` para que el administrador quede promovido.

**Qué protege.** El servicio `analytics` valida el token contra `users` y exige `role = admin` en todas
las rutas menos `/health`. Ocultar la pestaña en el frontend es solo comodidad: una petición directa
sin rol recibe `403`.

# 8. Verificación
