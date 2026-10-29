# Diccionario de datos: FitTrack-Synth

Dataset **sintético** de seguimiento físico (usuarios, medidas corporales, metas y rutinas), generado con
`generar_dataset.py`. Cubre 78 semanas, del 2025-01-06 al 2026-07-05. Los datos son ficticios: ninguna
persona, correo ni medida es real.

Los archivos contienen **datos crudos** con suciedad controlada (ver el final). El progreso hacia las metas
**no** viene en el dataset: se calcula con Spark.

## usuarios.csv (una fila por usuario)

| Columna | Tipo | Descripción |
|---|---|---|
| `user_id` | texto (UUID v4) | Identificador del usuario. Es la llave que une las demás tablas |
| `email` | texto | Correo ficticio (`usuarioNNNNNNN@fittrack.test`) |
| `fecha_nacimiento` | fecha `aaaa-mm-dd` | Fecha de nacimiento (edades de 18 a 65 años al registrarse) |
| `genero` | texto | `F`, `M` u `O` (otro) |
| `ciudad` | texto | Una de 10 ciudades de Colombia |
| `altura_cm` | decimal | Altura en centímetros |
| `fecha_registro` | fecha `aaaa-mm-dd` | Día en que el usuario se registró |
| `objetivo_fitness` | texto | `bajar_peso`, `ganar_musculo`, `mantener` o `resistencia` |
| `unidad_peso` | texto | `kg` o `lb`: la unidad en que este usuario registra su **peso** (en `medidas.peso` y en las metas de tipo `peso`) |

## medidas.csv (una fila por medición)

| Columna | Tipo | Descripción |
|---|---|---|
| `medida_id` | entero | Identificador de la medición |
| `user_id` | texto | Usuario (llave hacia `usuarios.csv`) |
| `fecha` | fecha | Normalmente `aaaa-mm-dd`; ~0,3 % de las filas vienen como `dd/mm/aaaa` |
| `peso` | decimal | Peso en la unidad del usuario (`unidad_peso`). Puede traer valores absurdos |
| `cintura` | decimal | Cintura en cm. ~3 % vacío |
| `brazo` | decimal | Brazo en cm. ~3 % vacío |
| `pecho` | decimal | Pecho en cm. ~3 % vacío |

## metas.csv (una fila por meta)

| Columna | Tipo | Descripción |
|---|---|---|
| `meta_id` | entero | Identificador de la meta |
| `user_id` | texto | Usuario (llave hacia `usuarios.csv`) |
| `tipo_medida` | texto | Medida que se quiere cambiar: `peso`, `cintura`, `brazo` o `pecho` |
| `valor_inicial` | decimal | Valor de esa medida al crear la meta (peso en la unidad del usuario; el resto en cm) |
| `valor_objetivo` | decimal | Valor que se quiere alcanzar (misma unidad que `valor_inicial`) |
| `direccion` | texto | `bajar` o `subir` |
| `fecha_creacion` | fecha | Día en que se creó la meta |
| `fecha_limite` | fecha | Día límite para alcanzarla |
| `estado` | texto | `cumplida`: se alcanzó el objetivo antes del límite. `vencida`: pasó el límite sin alcanzarlo y el usuario seguía activo. `abandonada`: el usuario dejó de registrar actividad antes de alcanzarla. `activa`: el límite cae después del final de los datos y el usuario sigue activo |

## rutinas.csv (una fila por sesión de entrenamiento)

| Columna | Tipo | Descripción |
|---|---|---|
| `rutina_id` | entero | Identificador de la sesión |
| `user_id` | texto | Usuario (llave hacia `usuarios.csv`) |
| `fecha` | fecha | Normalmente `aaaa-mm-dd`; ~0,3 % vienen como `dd/mm/aaaa` |
| `nombre` | texto | Nombre de la rutina (tipo y grupo muscular) |
| `tipo_enfoque` | texto | `fuerza`, `cardio`, `hiit`, `movilidad` o `mixto` |
| `grupo_muscular` | texto | `pecho`, `espalda`, `piernas`, `hombros`, `brazos`, `core` o `cuerpo_completo` |
| `duracion_min` | entero | Duración en minutos (15 a 120) |
| `num_ejercicios` | entero | Cantidad de ejercicios |
| `intensidad` | entero | Intensidad percibida, de 1 a 10 |

## Suciedad controlada (para la etapa de limpieza)

| Problema | Dónde | Cantidad aproximada |
|---|---|---|
| Filas duplicadas (copia exacta, mismo id) | `medidas.csv`, `rutinas.csv` | 0,5 % |
| Valores vacíos | `cintura`, `brazo`, `pecho` | 3 % de cada columna |
| Pesos absurdos (cero, negativos o multiplicados por 10) | `medidas.peso` | 0,1 % |
| Fechas en formato `dd/mm/aaaa` | `medidas.fecha`, `rutinas.fecha` | 0,3 % |
| Peso en libras en vez de kilos | `medidas.peso` y metas de peso | usuarios con `unidad_peso = lb` (~15 %) |

El conteo exacto de lo inyectado queda en `clave_respuestas/metadatos.json`.

## clave_respuestas/ (no usar en el pipeline)

Información oculta que **solo sirve para validar** que el análisis recupera lo que el generador sembró:

- `usuarios_ocultos.csv`: `user_id`, `constancia` (0 a 1), `sensibilidad` (respuesta del cuerpo al entrenamiento),
  `abandono_temprano` (si abandonó en las primeras 12 semanas), `semana_primera_inactiva` (semana en que dejó de
  registrar actividad; -1 si nunca dejó) y `peso_inicial_kg`.
- `metadatos.json`: parámetros usados, filas por archivo y suciedad inyectada.
