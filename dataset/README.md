# FitTrack-Synth: dataset sintético de seguimiento físico

Esta carpeta contiene el **generador** y el **validador** del dataset que alimenta el análisis con Spark de
FitTrack. El dataset es **sintético** (no hay datos de personas reales) y se genera con un script
**reproducible**: con la misma semilla y los mismos parámetros salen exactamente los mismos archivos.

Genera cuatro CSV (`usuarios`, `medidas`, `metas`, `rutinas`) y una carpeta `clave_respuestas/` con la
información oculta usada para validar. Las columnas están descritas en [`diccionario_datos.md`](diccionario_datos.md).

## Qué simula

Cada usuario tiene un perfil oculto (constancia, peso y altura iniciales, objetivo y probabilidad de abandonar).
Semana a semana, durante 78 semanas (2025-01-06 a 2026-07-05), se simulan sus sesiones de entrenamiento y sus
mediciones. Esto siembra patrones que el análisis debe poder descubrir:

- A más sesiones por semana, más cambio de peso (baja para `bajar_peso`, sube para `ganar_musculo`).
- Cerca de un tercio de los usuarios abandona en las primeras 12 semanas, sobre todo los poco constantes.
- Pico de registros y de actividad en enero.
- Las metas ambiciosas se cumplen menos.

Los parámetros del modelo (distribuciones de peso, altura, duración de rutinas, etc.) están al inicio de
`generar_dataset.py`. El progreso hacia las metas no se genera: lo calcula Spark.

## Requisitos

- **Con Docker (recomendado):** Docker y conexión a internet para construir la imagen (descarga `python:3.12-slim` y dos librerías).
- **Sin Docker:** Python 3.12 y `pip install -r requirements.txt`.
- Espacio en disco y memoria según el tamaño (ver la tabla de más abajo).

## 1. Generar el dataset (con Docker)

Desde esta carpeta (`dataset/`):

```bash
docker build -t fittrack-synth .
mkdir -p data
docker run --rm --user "$(id -u):$(id -g)" -v "$(pwd)/data:/data" fittrack-synth \
  generar_dataset.py --salida /data --usuarios 20000
```

Qué hace: el primer comando construye la imagen con el generador, el segundo crea la carpeta `data/` y el tercero
corre el generador dentro del contenedor y escribe los archivos en `data/`. Al terminar imprime un resumen (filas
por archivo y suciedad inyectada).

Sin Docker:

```bash
pip install -r requirements.txt
python3 generar_dataset.py --salida data --usuarios 20000
```

### Parámetros

| Parámetro | Por defecto | Descripción |
|---|---|---|
| `--usuarios` | 10000 | Número de usuarios. Es la escala del dataset |
| `--semilla` | 42 | Semilla aleatoria. Misma semilla y mismos parámetros dan el mismo dataset |
| `--salida` | `data` | Carpeta donde se escriben los archivos |
| `--bloque` | 2000 | Usuarios generados por bloque (controla la memoria). **No lo cambies si quieres reproducir un dataset**: cambia los datos |

## 2. Validar el dataset

```bash
docker run --rm -v "$(pwd)/data:/data" fittrack-synth validar_dataset.py --dir /data
```

(Sin Docker: `python3 validar_dataset.py --dir data`.) Revisa 24 puntos: que las filas coincidan con lo generado,
que todas las tablas se relacionen bien por `user_id`, que la suciedad inyectada sea la registrada y que los
patrones sembrados aparezcan. Debe terminar con `24 chequeos OK, 0 con falla`. Si algo falla, termina con código 1.

## Tamaños de referencia

| `--usuarios` | Filas aprox. | Peso en disco | Tiempo de generación | Fuente |
|---|---|---|---|---|
| 2.000 | 173 mil | 15 MB | 1 s | medido |
| 20.000 | 1,7 millones | 148 MB | 9 s | medido |
| 100.000 | 8,5 millones | 741 MB | 44 s | medido |
| 500.000 | ~42 millones | ~3,7 GB | ~4 min | estimado |

Los tiempos son de una máquina de 1 vCPU; el generador usa unos 275 MB de memoria en cualquier tamaño porque
trabaja por bloques. El **validador** carga todo en memoria: unos 450 MB con 20.000 usuarios y unos 2 GB por
cada 100.000.

## Archivos generados

```
data/
├── usuarios.csv
├── medidas.csv
├── metas.csv
├── rutinas.csv
└── clave_respuestas/        <- solo para validar; no usar en el análisis
    ├── usuarios_ocultos.csv
    └── metadatos.json
```

## Solución de problemas

- **`permission denied` al escribir en `data/`:** crea la carpeta antes (`mkdir -p data`) y deja la opción `--user "$(id -u):$(id -g)"` del comando.
- **`docker: command not found`:** instala Docker o usa la opción sin Docker.
- **El validador se queda sin memoria:** el dataset es muy grande para tu máquina; valida uno más pequeño (por ejemplo `--usuarios 20000`).
- **Quiero otro dataset distinto:** cambia `--semilla`. Para repetir el mismo, usa la misma semilla y los mismos parámetros.
