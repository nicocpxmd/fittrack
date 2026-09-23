# Contrato de API — Measurements

**Servicio:** measurements
**Stack:** FastAPI + MongoDB Atlas (Motor)
**Base URL local:** `http://localhost:8001` (variable de entorno `MEASUREMENTS_SERVICE_URL`)
**Prefijo de rutas:** `/measurements`

---

## Formato de error

Todos los errores controlados devuelven el formato estándar de FastAPI:

```json
{ "detail": "mensaje del error" }
```

## Modelo de datos — `measurements` (objeto anidado, se repite en varios endpoints)

Todos los campos son numéricos (float) y **opcionales** — cualquiera puede venir en `null` o ausente:

```json
{
  "weight_kg": 72.5,
  "height_cm": 178,
  "neck_cm": 38,
  "shoulder_cm": 110,
  "chest_cm": 95,
  "arm_cm": 32,
  "forearm_cm": 27,
  "waist_cm": 80,
  "abdomen_cm": 82,
  "hip_cm": 96,
  "upper_leg_cm": 55,
  "lower_leg_cm": 38,
  "calf_cm": 36
}
```

## Enums

**`date_confidence`** (default: `"exact"`) — indica qué tan precisa es la fecha del registro:
- `exact` — fecha exacta conocida
- `month_only` — solo se conoce mes y año
- `year_only` — solo se conoce el año

**`data_context`** (default: `"adult_baseline"`) — contexto biológico del dato:
- `adolescent_growth`
- `transition`
- `adult_baseline`

---

## Endpoints

### `POST /measurements/`

**Qué hace:** crea un nuevo registro de medidas.

**Request body:**
```json
{
  "date": "2026-09-23",
  "date_confidence": "exact",
  "data_context": "adult_baseline",
  "measurements": { "weight_kg": 72.5, "waist_cm": 80 },
  "notes": "opcional, string libre"
}
```
`date` es un string libre sin validación de formato por el modelo (se recomienda ISO 8601 `YYYY-MM-DD`); `date_confidence`, `data_context` y `notes` son opcionales con los valores por defecto ya indicados. `measurements` es obligatorio (puede venir con todos sus campos internos en `null`).

**Response 201:**
```json
{ "id": "651f3a2b9c1d4e5f6a7b8c9d" }
```
No devuelve el registro completo, solo el `id` generado por Mongo.

**Errores:**
- `422` — si falta `date` o `measurements`, o algún tipo de dato no corresponde (validación automática de Pydantic/FastAPI).

---

### `GET /measurements/`

**Qué hace:** devuelve todos los registros, ordenados por `date` ascendente.

**Request:** sin parámetros — no hay filtros ni paginación implementados todavía.

**Response 200:**
```json
[
  {
    "id": "651f3a2b9c1d4e5f6a7b8c9d",
    "date": "2026-09-23",
    "date_confidence": "exact",
    "data_context": "adult_baseline",
    "measurements": { "weight_kg": 72.5, "waist_cm": 80 },
    "notes": ""
  }
]
```

**Errores:** ninguno controlado.

> ⚠️ Límite conocido: el query trae como máximo 500 registros (`to_list(500)`). Si el dataset crece más que eso, hace falta agregar paginación — no implementada aún.

---

### `GET /measurements/{id}`

**Qué hace:** devuelve un registro puntual por su `id`.

**Request:** `id` en la URL (ObjectId de Mongo en formato string, 24 caracteres hex).

**Response 200:** mismo formato que un elemento de la lista de `GET /measurements/`.

**Errores:**
- `404` — `{ "detail": "Record not found" }` si el `id` es válido pero no existe.
- `500` — si `id` no tiene formato de ObjectId válido (no está validado, no devuelve un 400 controlado). *Limitación conocida.*

---

### `PUT /measurements/{id}`

**Qué hace:** actualiza parcialmente los campos dentro de `measurements` de un registro existente. **Solo el objeto `measurements`** — no permite modificar `date`, `date_confidence`, `data_context` ni `notes` por este endpoint.

**Request body:**
```json
{
  "measurements": { "weight_kg": 73.1 }
}
```
Solo hace falta incluir los campos que se quieren actualizar; los que no se envían quedan intactos en la base de datos (usa `$set` con dot notation, no reemplaza el objeto completo).

**Response 200:**
```json
{ "updated": true }
```

**Errores:**
- `400` — `{ "detail": "No update data provided" }` si `measurements` viene vacío o con todos los campos en `null`.
- `404` — `{ "detail": "Record not found" }` si el `id` no existe.
- `500` — mismo caso de ObjectId inválido que en GET por id. *Limitación conocida.*

---

### `DELETE /measurements/{id}`

**Qué hace:** elimina un registro.

**Request:** `id` en la URL.

**Response 204:** sin body.

**Errores:**
- `404` — `{ "detail": "Record not found" }` si no existe.
- `500` — mismo caso de ObjectId inválido. *Limitación conocida.*
