# Contrato de API — Goals

**Servicio:** goals  
**Stack:** Node.js + Express + MySQL  
**Base URL local:** `http://localhost:8004` (variable de entorno `GOALS_PORT`)  
**Prefijo de rutas:** `/goals`

## Formato de error

```json
{ "error": "mensaje del error" }
```

---

## Endpoints

### `POST /goals`
* **Qué hace:** Valida el token JWT del usuario con el servicio `Users`, y si es válido, crea una nueva meta vinculada a su `user_id`.
* **Headers requeridos:**
  * `Authorization`: `Bearer <token_jwt>`
* **Request body:**
  ```json
  {
    "tipo_meta": "rutina",
    "descripcion": "Completar 10 rutinas este mes",
    "valor_objetivo": 10.0,
    "fecha_limite": "2026-10-31"
  }
  ```
* **Response 201:**
  ```json
  {
    "mensaje": "Meta creada exitosamente",
    "id": 1
  }
  ```
* **Errores:**
  * `400` — `{ "error": "Faltan datos obligatorios." }`
  * `401` — `{ "error": "No autorizado. Token inválido o expirado." }`
  * `500` — `{ "error": "Error interno del servidor." }`

---

### `GET /goals`
* **Qué hace:** Devuelve una lista de todas las metas creadas por el usuario autenticado.
* **Headers requeridos:**
  * `Authorization`: `Bearer <token_jwt>`
* **Response 200:**
  ```json
  [
    {
      "id": 1,
      "user_id": "uuid-del-usuario",
      "tipo_meta": "rutina",
      "descripcion": "Completar 10 rutinas este mes",
      "valor_objetivo": "10.00",
      "fecha_limite": "2026-10-31T05:00:00.000Z",
      "created_at": "2026-09-24T10:00:00.000Z"
    }
  ]
  ```
* **Errores:**
  * `401` — `{ "error": "No autorizado o error al consultar metas." }`

---

### `GET /goals/{id}`
* **Qué hace:** Obtiene los detalles de una meta específica y consulta dinámicamente el progreso actual comunicándose con el microservicio de `Workouts` (si es meta de rutina) o `Progress` (si es meta de medida corporal) para calcular el porcentaje de cumplimiento.
* **Response 200:**
  ```json
  {
    "id": 1,
    "user_id": "uuid-del-usuario",
    "tipo_meta": "rutina",
    "descripcion": "Completar 10 rutinas este mes",
    "valor_objetivo": "10.00",
    "fecha_limite": "2026-10-31T05:00:00.000Z",
    "created_at": "2026-09-24T10:00:00.000Z",
    "valor_actual": 4,
    "porcentaje_cumplimiento": 40.0,
    "cumplida": false
  }
  ```
* **Errores:**
  * `404` — `{ "error": "Meta no encontrada." }`
  * `500` — `{ "error": "Error interno." }`

---

### `PUT /goals/{id}`
* **Qué hace:** Permite actualizar los campos de una meta existente. Valida que la meta pertenezca al usuario autenticado.
* **Headers requeridos:**
  * `Authorization`: `Bearer <token_jwt>`
* **Request body (envía solo los campos a modificar):**
  ```json
  {
    "descripcion": "Completar 15 rutinas este mes",
    "valor_objetivo": 15.0
  }
  ```
* **Response 200:**
  ```json
  {
    "mensaje": "Meta actualizada con éxito."
  }
  ```
* **Errores:**
  * `401` — `{ "error": "No autorizado. Token inválido o expirado." }`
  * `403` — `{ "error": "Sin permiso." }`
  * `404` — `{ "error": "No existe la meta." }`

---

### `DELETE /goals/{id}`
* **Qué hace:** Elimina una meta de la base de datos. Requiere que la meta pertenezca al usuario autenticado.
* **Headers requeridos:**
  * `Authorization`: `Bearer <token_jwt>`
* **Response 200:**
  ```json
  {
    "mensaje": "Meta eliminada."
  }
  ```
* **Errores:**
  * `401` — `{ "error": "No autorizado. Token inválido o expirado." }`
  * `403` — `{ "error": "Sin permiso." }`
  * `404` — `{ "error": "Meta no encontrada." }`

---

## Instrucciones paso a paso para correrlo localmente

1. Abre una terminal y sitúate en la carpeta del servicio:
   ```bash
   cd services/goals
   ```
   *(Nota: si lo ubicaste dentro de una subcarpeta, usa `cd services/goals/app`)*.

2. Instala las dependencias del proyecto:
   ```bash
   npm install
   ```

3. Copia `.env.example` a `.env` y ajusta tus credenciales de MySQL y las URLs de los otros servicios (Users, Progress, Workouts):
   * **Windows (CMD/PowerShell):** 
     ```bash
     copy .env.example .env
     ```
   * **Mac/Linux/Git Bash:** 
     ```bash
     cp .env.example .env
     ```

4. Asegúrate de tener tu base de datos MySQL corriendo y que la tabla `goals` esté creada según el archivo `schema.sql`.

5. Arranca el servicio en el puerto 8004 con recarga automática:
   ```bash
   node --watch src/index.js
   ```
   *(O usa `npm run dev` si configuraste ese script en tu `package.json`)*.