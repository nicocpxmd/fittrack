# Contrato de API — Users

**Servicio:** users
**Stack:** FastAPI + PostgreSQL
**Base URL local:** `http://localhost:8002` (variable de entorno `USERS_SERVICE_URL`)
**Prefijo de rutas:** `/users`

## Formato de error

Todos los errores controlados devuelven el formato estándar de FastAPI:

```
{ "detail": "mensaje del error" }

```

## Modelos de Datos Relevantes

**`gender`** (opcional):

* `M`, `F`, `other`, `prefer_not_to_say`

**`fitness_goal`** (opcional):

* `weight_loss`, `muscle_gain`, `maintenance`, `endurance`

**`preferred_units`** (default: `"metric"`):

* `metric` (kg, cm), `imperial` (lbs, in)

## Endpoints de Autenticación y Registro

### `POST /users/register`

**Qué hace:** Crea un nuevo perfil de usuario con datos enfocados a fitness.

**Request body:**

```
{
  "email": "usuario@ejemplo.com",
  "password": "PasswordSeguro123",
  "full_name": "Juan Camilo",
  "date_of_birth": "2006-05-15", 
  "gender": "M",
  "fitness_goal": "muscle_gain",
  "preferred_units": "metric"
}

```

**Response 201:**

```
{
  "id": "uuid-v4-generado-por-postgres",
  "email": "usuario@ejemplo.com",
  "full_name": "Juan Camilo",
  "date_of_birth": "2006-05-15",
  "gender": "M",
  "fitness_goal": "muscle_gain",
  "preferred_units": "metric",
  "created_at": "2026-09-23T16:00:00Z"
}

```

**Errores:**

* `400` — `{ "detail": "Email already registered" }`

* `422` — Error de validación de Pydantic (ej. formato de fecha incorrecto, contraseña muy corta).

### `POST /users/login`

**Qué hace:** Autentica al usuario y devuelve un token de acceso (JWT).

**Request body** (Formato JSON simple):

```
{
  "email": "usuario@ejemplo.com",
  "password": "PasswordSeguro123"
}

```

**Response 200:**

```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}

```

**Errores:**

* `401` — `{ "detail": "Incorrect email or password" }`

## Endpoints de Perfil

### `GET /users/me`

**Qué hace:** Devuelve los datos del usuario autenticado.

**Headers requeridos:**
`Authorization: Bearer <access_token>`

**Response 200:**

```
{
  "id": "uuid-v4-generado-por-postgres",
  "email": "usuario@ejemplo.com",
  "full_name": "Juan Camilo",
  "date_of_birth": "2006-05-15",
  "gender": "M",
  "fitness_goal": "muscle_gain",
  "preferred_units": "metric",
  "created_at": "2026-09-23T16:00:00Z"
}

```

**Errores:**

* `401` — `{ "detail": "Could not validate credentials" }`

### `PUT /users/me`

**Qué hace:** Actualiza parcialmente el perfil del usuario autenticado (edición de perfil).

**Headers requeridos:**
`Authorization: Bearer <access_token>`

**Request body** (todos los campos son opcionales, envía solo los que cambian):

```
{
  "full_name": "Juan Camilo S.",
  "fitness_goal": "maintenance",
  "preferred_units": "metric"
}

```

**Response 200:**

```
{
  "updated": true,
  "user": {
    "id": "uuid-v4-generado-por-postgres",
    "email": "usuario@ejemplo.com",
    "full_name": "Juan Camilo S.",
    "date_of_birth": "2006-05-15",
    "gender": "M",
    "fitness_goal": "maintenance",
    "preferred_units": "metric",
    "created_at": "2026-09-23T16:00:00Z"
  }
}

```

**Errores:**

* `400` — `{ "detail": "No update data provided" }`

* `401` — `{ "detail": "Could not validate credentials" }`

## Endpoints de Recuperación de Contraseña

### `POST /users/password-recovery`

**Qué hace:** Solicita un token de recuperación al correo del usuario. (Actualmente simula el envío y genera el token en BD).

**Request body:**

```
{
  "email": "usuario@ejemplo.com"
}

```

**Response 202 (Accepted):**

```
{ "message": "If the email exists, a recovery link has been sent." }

```

### `POST /users/password-reset`

**Qué hace:** Establece una nueva contraseña utilizando el token temporal generado en la ruta anterior.

**Request body:**

```
{
  "token": "token-temporal-enviado-por-email",
  "new_password": "NuevoPasswordSeguro456"
}

```

**Response 200:**

```
{ "message": "Password updated successfully" }

```

**Errores:**

* `400` — `{ "detail": "Invalid or expired token" }`