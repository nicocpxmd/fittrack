# Contrato de API — Progress

**Servicio:** progress  
**Stack:** FastAPI + MongoDB (Motor)  
**Base URL local:** `http://localhost:8005` (variable de entorno `PROGRESS_SERVICE_URL`)  
**Prefijo de rutas:** `/progress`

## Formato de error

```json
{ "detail": "mensaje del error" }
```

---

## Endpoints

### `POST /progress/calculate`
* **Qué hace:** Consulta los datos de measurements, calcula el valor inicial, actual y la diferencia en un rango de fechas, y guarda un snapshot real en base de datos.
* **Request body:**
  ```json
  {
    "user_id": "uuid-o-id-de-usuario",
    "tipo_medida": "weight_kg",
    "desde": "2026-01-01",
    "hasta": "2026-09-23"
  }
  ```
* **Response 201:**
  ```json
  {
    "id": "651f3a2b9c1d4e5f6a7b8c9d",
    "user_id": "uuid-o-id-de-usuario",
    "tipo_medida": "weight_kg",
    "valor_inicial": 75.0,
    "valor_actual": 72.5,
    "diferencia": -2.5,
    "fecha_inicio": "2026-01-10",
    "fecha_fin": "2026-09-20",
    "created_at": "2026-09-23T21:00:00Z"
  }
  ```
* **Errores:**
  * `404` — `{ "detail": "No measurements found for type '...' in the specified range." }`
  * `502 / 503` — Si el servicio measurements no responde.

---

### `GET /progress/{user_id}`
* **Qué hace:** Devuelve todos los snapshots de progreso ya calculados y guardados para un usuario específico.
* **Response 200:**
  ```json
  [
    {
      "id": "651f3a2b9c1d4e5f6a7b8c9d",
      "user_id": "uuid-o-id-de-usuario",
      "tipo_medida": "weight_kg",
      "valor_inicial": 75.0,
      "valor_actual": 72.5,
      "diferencia": -2.5,
      "fecha_inicio": "2026-01-10",
      "fecha_fin": "2026-09-20",
      "created_at": "2026-09-23T21:00:00Z"
    }
  ]
  ```

---

## Instrucciones paso a paso para correrlo localmente

1. Abre una terminal y sitúate en la carpeta del servicio:
   ```bash
   cd services/progress
   ```

2. Crea tu entorno virtual:
   ```bash
   python -m venv venv --copies
   ```

3. Activa el entorno virtual:
   * **Windows:** 
     ```bash
     venv\Scripts\activate
     ```
   * **Mac/Linux:** 
     ```bash
     source venv/bin/activate
     ```

4. Instala las dependencias:
   ```bash
   python -m pip install -r requirements.txt
   ```

5. Copia `.env.example` a `.env` y ajusta tu conexión a MongoDB Atlas y los puertos de los otros servicios:
   * **Windows:** 
     ```bash
     copy .env.example .env
     ```
   * **Mac/Linux:** 
     ```bash
     cp .env.example .env
     ```

6. Arranca el servicio en el puerto 8005:
   ```bash
   python -m uvicorn main:app --reload --port 8005