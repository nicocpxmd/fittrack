# Goals: guia de cambios e integracion

## Resumen

El microservicio `goals` administra metas personales y calcula su estado actual consultando otros microservicios por HTTP.

La configuracion local esperada es:

| Servicio | Puerto |
|---|---:|
| users | 8002 |
| workouts | 8003 |
| goals | 8004 |
| progress | 8005 |
| measurements | 8001 |

## Cambios principales

### `user_id` explicito

Las rutas de `goals` ya no requieren el header `Authorization`. El `user_id` debe enviarse explicitamente:

- En el body para `POST /goals`.
- En el query string para `GET /goals`.
- En el query string para `GET /goals/:id`.
- En el body para `PUT /goals/:id`.
- En el query string para `DELETE /goals/:id`.

El servicio verifica que el `user_id` recibido coincida con el usuario propietario de la meta en las operaciones sobre una meta especifica.

> Esta modalidad es util para pruebas locales, pero no reemplaza una autenticacion real. Un cliente puede enviar un `user_id` arbitrario porque `goals` ya no valida un token contra `users`.

## Endpoints

### Crear una meta

```http
POST http://localhost:8004/goals
Content-Type: application/json
```

Body:

```json
{
  "user_id": "ID_DEL_USUARIO",
  "tipo_meta": "weight_kg",
  "descripcion": "Alcanzar peso objetivo",
  "valor_objetivo": 70,
  "fecha_limite": "2026-12-31"
}
```

Respuesta esperada (`201`):

```json
{
  "mensaje": "Meta creada exitosamente",
  "id": 1
}
```

Campos obligatorios:

- `user_id`
- `tipo_meta`
- `descripcion`
- `valor_objetivo`
- `fecha_limite`

### Listar metas de un usuario

```http
GET http://localhost:8004/goals?user_id=ID_DEL_USUARIO
```

Sin `user_id`, responde `400`.

### Consultar una meta y calcular su progreso

```http
GET http://localhost:8004/goals/ID_DE_LA_META?user_id=ID_DEL_USUARIO
```

La respuesta agrega:

```json
{
  "valor_actual": 72.5,
  "porcentaje_cumplimiento": 100,
  "cumplida": true
}
```

Si el `user_id` no coincide con el propietario de la meta, responde `403`.

### Listar todas las metas (administracion)

```http
GET http://localhost:8004/goals/admin/all
```

Esta ruta no filtra por usuario.

### Actualizar una meta

```http
PUT http://localhost:8004/goals/ID_DE_LA_META
Content-Type: application/json
```

Body:

```json
{
  "user_id": "ID_DEL_USUARIO",
  "tipo_meta": "weight_kg",
  "descripcion": "Nuevo objetivo de peso",
  "valor_objetivo": 68,
  "fecha_limite": "2026-12-31"
}
```

`user_id` es obligatorio aunque solo se quiera modificar otro campo.

### Eliminar una meta

```http
DELETE http://localhost:8004/goals/ID_DE_LA_META?user_id=ID_DEL_USUARIO
```

## Integraciones

### Metas de medidas corporales

Para metas como `weight_kg`, `height_cm` o `waist_cm`, el flujo es:

```text
goals -> progress -> measurements
```

Al consultar una meta, `goals` llama a:

```http
POST http://localhost:8005/progress/calculate
```

Con un body equivalente a:

```json
{
  "user_id": "ID_DEL_USUARIO",
  "tipo_medida": "weight_kg",
  "desde": "2026-01-01",
  "hasta": "2026-12-31"
}
```

`progress` consulta `measurements`, calcula el valor inicial, el valor actual y la diferencia, y guarda un snapshot.

Si `progress` no responde, `goals` intenta consultar directamente:

```http
GET http://localhost:8001/measurements/
```

### Metas de rutinas

Para una meta con:

```json
{
  "tipo_meta": "rutina"
}
```

El flujo es:

```text
goals -> workouts
```

`goals` consulta:

```http
GET http://localhost:8003/api/routines
```

El `valor_actual` es la cantidad de rutinas devueltas por `workouts`.

## Calculo actual

El porcentaje se calcula actualmente como:

```text
porcentaje_cumplimiento = min(100, (valor_actual / valor_objetivo) * 100)
```

La meta se marca como cumplida cuando:

```text
valor_actual >= valor_objetivo
```

Esto funciona para objetivos crecientes, como completar 5 rutinas. Para objetivos de reduccion, como bajar de 80 kg a 70 kg, la regla debera definirse posteriormente.

## Prueba recomendada en Thunder Client

1. Crear o identificar un usuario en `users` y copiar su `id`.
2. Crear una medicion en `measurements` si la meta es corporal.
3. Crear una meta en `goals` usando ese `user_id`.
4. Consultar `GET /goals/:id?user_id=...`.
5. Revisar que `valor_actual` provenga de `progress`.
6. Consultar `GET /progress/:user_id` para comprobar el snapshot.

Para una meta de rutina:

1. Crear una rutina en `workouts`.
2. Crear en `goals` una meta con `tipo_meta: "rutina"`.
3. Consultar la meta.
4. Confirmar que `valor_actual` coincide con la cantidad de rutinas.

## Arranque

Desde `services/goals`:

```powershell
node src/index.js
```

El servicio queda disponible en:

```text
http://localhost:8004
```

Los archivos `.env` reales son locales y no deben subirse al repositorio. Usa `.env.example` como referencia de las URLs entre servicios.
