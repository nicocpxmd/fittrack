# Consistencia entre el dataset y la aplicación FitTrack

Estado: 2026-11-06. Dataset: **FitTrack-Synth** (100.000 usuarios, 8.462.080 filas).
Aplicación: microservicios de `services/` y dashboard de `frontend/`.

Este documento compara el esquema del dataset con el esquema real de la aplicación. La conclusión
principal es que el dataset es **analítico**, no un volcado de las bases operativas: el ETL traduce
nombres, unidades, fechas y estados, y el dashboard consume agregados por una API. No se cargan los
100.000 usuarios en las bases de la app.

## 1. Dos campos que se confunden

| Campo | Dónde vive | Valores | Qué significa |
|---|---|---|---|
| `objetivo_fitness` | `usuarios.csv` | `bajar_peso`, `ganar_musculo`, `mantener`, `resistencia` | Objetivo global del usuario (perfil) |
| `direccion` | `metas.csv` y `goals.direccion` | `subir`, `bajar` | Dirección de una meta concreta |

La app ya tiene el equivalente del primero en `FitnessGoalEnum` (`services/users/app/schemas.py`):

| Dataset | App (`fitness_goal`) |
|---|---|
| `bajar_peso` | `weight_loss` |
| `ganar_musculo` | `muscle_gain` |
| `mantener` | `maintenance` |
| `resistencia` | `endurance` |

El segundo coincide exactamente con el enum de MySQL `goals.direccion('subir','bajar')`. Por eso en
el formulario de metas solo se ven **subir/bajar**: es la dirección de esa meta, no el objetivo del
usuario. Los cuatro objetivos son una dimensión de análisis (cambio de peso y cumplimiento de metas
por objetivo), no una alternativa a subir/bajar.

La app acepta `fitness_goal` en `UserCreate` y en `PUT /users/me`, pero el HTML actual no lo pide; en
la app real queda `null` hasta que se agregue un campo de perfil.

## 2. Mapeo por entidad

### 2.1 Usuarios (`usuarios.csv` → `users`)

| Dataset | App | Estado |
|---|---|---|
| `user_id` | `id` (String UUID) | ✅ compatible |
| `email` | `email` (`EmailStr`) | ⚠️ `@fittrack.test` es dominio reservado y el validador lo rechaza |
| `fecha_nacimiento` | `date_of_birth` | ✅ |
| `genero` (`F`, `M`, `O`) | `gender` (`M`, `F`, `other`, `prefer_not_to_say`) | ⚠️ mapear `O → other` |
| `ciudad` | no existe en `users` | ⚠️ solo analítico |
| `altura_cm` | no está en `users`; va en `measurements.height_cm` | ⚠️ mapear a una medida |
| `fecha_registro` | `created_at` | ✅ |
| `objetivo_fitness` | `fitness_goal` | ⚠️ mapear español → inglés |
| `unidad_peso` (`kg`, `lb`) | `preferred_units` (`metric`, `imperial`) | ⚠️ mapear |
| — | `password` / `password_hash` | ❌ falta en el dataset |
| — | `full_name` | ❌ falta en el dataset |

### 2.2 Medidas (`medidas.csv` → `measurements`, Mongo)

| Dataset | App | Estado |
|---|---|---|
| `medida_id` | `_id` (ObjectId) | ⚠️ no se conserva; Mongo genera otro |
| `user_id` | `user_id` | ✅ |
| `fecha` (ISO o `dd/mm/aaaa`) | `date` (ISO) | ⚠️ normalizar; la app exige `YYYY-MM-DD` |
| `peso` (unidad del usuario) | `measurements.weight_kg` | ⚠️ convertir lb→kg; `gt=0` rechaza 0/negativos |
| `cintura` | `measurements.waist_cm` | ⚠️ renombrar; nulos permitidos |
| `brazo` | `measurements.arm_cm` | ⚠️ renombrar |
| `pecho` | `measurements.chest_cm` | ⚠️ renombrar |
| — | `height_cm`, `neck_cm`, `shoulder_cm`, etc. | ✅ opcionales; el dataset cubre 4 de 13 |
| — | `date_confidence`, `data_context`, `notes` | ✅ la app pone defaults |

### 2.3 Metas (`metas.csv` → `goals`, MySQL)

| Dataset | App | Estado |
|---|---|---|
| `meta_id` | `id` autoincremental | ⚠️ preservar o dejar que MySQL asigne |
| `user_id` | `user_id` | ✅ |
| `tipo_medida` (`peso`, `cintura`, `brazo`, `pecho`) | `tipo_meta` (`weight_kg`, `waist_cm`, `arm_cm`, `chest_cm`) | ⚠️ mapear; con `peso` el servicio progress devuelve 404 |
| `valor_inicial` | `valor_inicial` | ⚠️ convertir lb→kg en metas de peso |
| `valor_objetivo` | `valor_objetivo` | ⚠️ convertir lb→kg |
| `direccion` (`subir`, `bajar`) | `direccion` enum (`subir`, `bajar`) | ✅ coincide |
| `fecha_creacion` | `created_at` | ✅ |
| `fecha_limite` | `fecha_limite` | ✅ |
| `estado` (`cumplida`, `vencida`, `abandonada`, `activa`) | `cumplida` boolean | ⚠️ mapear `cumplida → 1`; los otros estados son analíticos |
| — | `descripcion` (NOT NULL) | ❌ falta en el dataset |
| — | `valor_actual`, `porcentaje_cumplimiento` | ⚠️ la app los calcula desde measurements |

La app calcula el porcentaje así: para `bajar`, cumple cuando `valor_actual <= valor_objetivo`; para
`subir`, cuando `valor_actual >= valor_objetivo`. El dataset usa la misma lógica para generar
`estado`, así que la semántica es consistente.

### 2.4 Rutinas (`rutinas.csv` → `routines`, MySQL)

| Dataset | App | Estado |
|---|---|---|
| `rutina_id` | `id` autoincremental | ⚠️ opcional preservar |
| `user_id` | `user_id` | ✅ |
| `fecha` | `fecha_creacion` (NOT NULL) | ⚠️ normalizar formato |
| `nombre` | `nombre_rutina` | ⚠️ renombrar |
| `tipo_enfoque` | `tipo_enfoque` | ✅ valores compatibles |
| `grupo_muscular` | `grupo_muscular` | ✅ valores compatibles |
| `duracion_min` | no existe | ⚠️ solo analítico |
| `num_ejercicios` | no existe | ⚠️ solo analítico |
| `intensidad` | no existe | ⚠️ solo analítico |
| — | `ejercicios` (texto) | ⚠️ falta en el dataset; puede quedar NULL |

### 2.5 Progreso

El dataset no tiene tabla de progreso: el progreso se calcula desde las medidas, igual que en la app
(`progress/calculate`). La única dependencia es que `tipo_medida` use los nombres de la app
(`weight_kg`, `waist_cm`, etc.); con `peso` falla.

## 3. Brechas si se quisiera cargar el dataset en la app

Cargar los CSV en las bases operativas **no es directo**. Habría que resolver, como mínimo:

1. Reescribir los correos `@fittrack.test` a un dominio que acepte `EmailStr`.
2. Generar `password`/`password_hash` y `full_name` para 100.000 usuarios.
3. Mapear `objetivo_fitness` → `fitness_goal` y `genero` → `gender`.
4. Mapear `unidad_peso` → `preferred_units` y convertir pesos lb→kg.
5. Decidir qué hacer con `ciudad` (no hay columna) y `altura_cm` (debe ir a measurements).
6. Normalizar fechas `dd/mm/aaaa` y filtrar pesos inválidos antes de insertar.
7. Mapear `tipo_medida` → `tipo_meta` (`peso` → `weight_kg`, etc.).
8. Generar `descripcion` para las metas; mapear `estado` → `cumplida`.
9. Decidir qué hacer con `duracion_min`, `num_ejercicios` e `intensidad` (no existen en `routines`).
10. Resolver los IDs: Mongo ObjectId para medidas y autoincrementales para metas/rutinas.

## 4. Decisión: el dataset no se carga en la app

El enunciado pide una **aplicación de análisis de datos** que genere reportes y que esos reportes
sean **tomados por la aplicación inicial para mostrarlos en un dashboard**. No pide volcar el dataset
en las bases operativas de la app.

Por eso el diseño es:

```text
CSV → Spark (ETL + KPIs) → analytics.json → API analytics → dashboard
```

- Las bases de la app siguen guardando datos de usuarios reales y de la cuenta de prueba.
- El dataset vive en el plano analítico, no en el transaccional.
- El dashboard consume `/api/analytics/*`; no consulta las tablas de la app.
- Si Spark está apagado, el dashboard sigue funcionando con el último JSON.

Ventajas:

- No se contaminan las bases operativas con 100.000 usuarios ficticios.
- No se rompen las validaciones de la app (email, `gt=0`, campos obligatorios).
- No se afectan rendimiento, backups ni aislamiento por usuario.
- El dashboard funciona sin Spark encendido.
- La correspondencia queda documentada y el ETL es el único punto de traducción.

Si se necesita un usuario de demostración con datos, se crea un **seed pequeño** (una cuenta con
unas pocas medidas, metas y rutinas) y se deja el dataset completo para Spark. No se cargan los
100.000 usuarios.

## 5. Cómo cumple el requisito

| Requisito del enunciado | Cómo se cumple |
|---|---|
| Dataset de fuente abierta / autorizado | `dataset/` con generador, validador y diccionario; autorizado por el profesor |
| Aplicación de análisis a gran escala | Spark procesa 8,4 M filas y genera reportes |
| Reportes tomados por la app | API `analytics` publica `/api/analytics/*` |
| Mostrados en un dashboard | Pestaña “Analítica” del frontend |
| Separación app/analítica | D18: JSON + API, sin JDBC ni carga en las bases |

## 6. Referencias

- `services/users/app/models.py` y `schemas.py` (`FitnessGoalEnum`, `GenderEnum`, `UnitsEnum`).
- `services/measurements/app/models.py` (`Measurements`, `MeasurementRecord`).
- `services/goals/schema.sql` y `src/controllers/goalsControllers.js` (dirección y porcentaje).
- `services/workouts/schema.sql` y `models/routinesModel.js`.
- `services/progress/app/routers/progress.py` (`tipo_medida`).
- `docs/decisiones.md` D18 (pipeline batch + JSON).
- `dataset/diccionario_datos.md` y `dataset/README.md`.
