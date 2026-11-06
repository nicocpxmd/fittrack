# FitTrack — Proyecto final de Infraestructura

Aplicación de seguimiento físico basada en microservicios, desplegada en un clúster Docker Swarm, más
un pipeline de análisis con Apache Spark que alimenta una pestaña de analítica en el dashboard.

El proyecto tiene dos partes:

1. **Contenedores y clúster:** seis microservicios, frontend, HAProxy y tres bases de datos en Swarm,
   con escalabilidad y balanceo.
2. **Procesamiento distribuido:** dataset sintético de 100.000 usuarios (8,4 M de filas), ETL y KPIs
   con Spark, y un dashboard que consume los resultados.

> El dataset es **sintético y reproducible**, autorizado por el profesor. No contiene datos de
> personas reales.

## Arquitectura

```text
Navegador
   │  http://192.168.100.2:8080
   ▼
HAProxy (clienteUbuntu) ── /api/* ──► users, measurements, progress, goals, workouts, analytics
   │                                   │
   └── / ──► nginx (frontend)          ├── Postgres (users)
                                       ├── Mongo (measurements, progress)
                                       ├── MySQL (workouts, goals)
                                       └── /data/analytics.json (analytics)

Spark (servidorUbuntu: master + worker)
   dataset/data ──► ETL ──► analytics/curated (Parquet) ──► analytics/data (JSON)
```

| Nodo | IP | Qué corre |
|---|---|---|
| `servidorUbuntu` | `192.168.100.3` | Swarm manager; microservicios, bases de datos, `analytics`, Spark master/worker |
| `clienteUbuntu` | `192.168.100.2` | Swarm worker; nginx y HAProxy |

## Requisitos

- Docker Engine con Swarm inicializado.
- Dos nodos unidos al Swarm (`docker node ls`).
- Spark 4.2.0 en `/root/labSpark/spark-4.2.0-bin-hadoop3` (servidor).
- Python 3.10+ para los jobs de Spark.
- Dataset generado en `/root/fittrack/dataset/data` (ver abajo).
- Acceso a Docker Hub para publicar/descargar las imágenes del namespace `nicocpxm`.

## Parte 1 — stack de contenedores

### 1. Variables de entorno

En `/root/fittrack`:

```bash
cp .env.example .env
# editar .env con valores reales
```

Variables:

| Variable | Uso |
|---|---|
| `POSTGRES_PASSWORD` | contraseña de Postgres (users) |
| `DB_PASSWORD` | contraseña root de MySQL (workouts, goals) |
| `SECRET_KEY` | firma de los JWT |

El `.env` **no se versiona**.

### 2. Imágenes

Las imágenes base ya están publicadas. Si se cambia el frontend, HAProxy o el servicio de analítica:

```bash
docker build -t nicocpxm/fittrack-nginx:v3 ./frontend
docker build -t nicocpxm/fittrack-haproxy:v2 ./haproxy
docker build -t nicocpxm/fittrack-analytics:v1 ./analytics
docker push nicocpxm/fittrack-nginx:v3
docker push nicocpxm/fittrack-haproxy:v2
docker push nicocpxm/fittrack-analytics:v1
```

### 3. Desplegar

```bash
cd /root/fittrack
set -a
. ./.env
set +a
docker stack deploy -c docker-stack.yml fittrack
docker stack services fittrack
```

Esperar a que los servicios estén `1/1`. El entrypoint es
`http://192.168.100.2:8080` y las stats de HAProxy están en `http://192.168.100.2:8404`
(usuario `admin`, contraseña `admin`).

### 4. Servicios

| Servicio | Puerto interno | Base |
|---|---|---|
| users | 8002 | Postgres |
| measurements | 8001 | Mongo |
| progress | 8005 | Mongo |
| workouts | 8003 | MySQL |
| goals | 8004 | MySQL |
| analytics | 8006 | JSON de Spark |
| nginx | 80 | frontend estático |
| haproxy | 80 / 8404 | entrada y stats |

## Parte 2 — pipeline Spark

### 1. Dataset

Generar 100.000 usuarios (si no existe):

```bash
cd /root/fittrack/dataset
docker build -t fittrack-synth .
mkdir -p data
docker run --rm -v "$PWD/data:/data" fittrack-synth \
  generar_dataset.py --salida /data --usuarios 100000 --semilla 42
docker run --rm -v "$PWD/data:/data" fittrack-synth \
  validar_dataset.py --dir /data
```

Debe terminar con **24 chequeos OK, 0 con falla**. Tamaño aproximado: 741 MB.

### 2. Arrancar Spark

```bash
cd /root/labSpark/spark-4.2.0-bin-hadoop3/sbin
./start-master.sh
./start-worker.sh spark://192.168.100.3:7077
```

Verificar en `http://192.168.100.3:8080`: **Alive Workers: 1**, **Cores in use: 4**.

### 3. ETL + KPIs

```bash
cd /root/fittrack
bash spark/run_all.sh
```

Salidas:

- `analytics/curated/`: Parquet limpio (`usuarios`, `medidas`, `rutinas`, `metas`).
- `analytics/data/cleaning.json`: conteos de limpieza.
- `analytics/data/analytics.json`: KPIs que consume el dashboard.

Resultados de referencia con 100.000 usuarios:

| Métrica | Valor |
|---|---|
| Usuarios | 100.000 |
| Filas curadas | 8.418.175 |
| Duplicados de medidas | 14.204 |
| Pesos inválidos | 2.925 |
| Duplicados de rutinas | 26.776 |
| Retención a 12 semanas | 51,63 % |
| Cumplimiento de metas | 16,96 % |
| Cambio promedio de peso | −0,71 kg |
| Correlación bajar peso | −0,595 |
| Correlación ganar músculo | +0,597 |
| Abandono temprano | 39,53 % |
| Pico de enero | 1,88× |

### 4. Publicar la analítica

```bash
cd /root/fittrack
docker build -t nicocpxm/fittrack-analytics:v1 ./analytics
docker build -t nicocpxm/fittrack-haproxy:v2 ./haproxy
docker build -t nicocpxm/fittrack-nginx:v3 ./frontend
docker push nicocpxm/fittrack-analytics:v1
docker push nicocpxm/fittrack-haproxy:v2
docker push nicocpxm/fittrack-nginx:v3
set -a; . ./.env; set +a
docker stack deploy -c docker-stack.yml fittrack
```

El servicio `analytics` monta `/root/fittrack/analytics/data` en `/data` (solo lectura). Si se vuelve
a correr Spark, la API toma el JSON nuevo sin reiniciar el contenedor (cache por `mtime`).

## Pruebas

### Humo

```bash
curl -s http://192.168.100.2:8080/ | head
curl -s http://192.168.100.2:8080/api/analytics/health
curl -s http://192.168.100.2:8080/api/analytics/kpis
```

### Carga

```bash
python tests/load/load_test.py \
  --base http://192.168.100.2:8080 \
  --email audit20261105@gmail.com \
  --password Password123 \
  --requests 500 --concurrency 20
```

Línea base medida con 1 réplica: **38,15 RPS**, p95 **654,58 ms**, 0 errores.
Para comparar, escalar `users` y `measurements` y repetir:

```bash
docker service scale fittrack_users=3 fittrack_measurements=3
```

### Validación del pipeline

El JSON de analítica incluye `validacion` con los patrones sembrados por el generador:

- abandono temprano ≈ 40 %,
- pico de enero ≥ 1,4×,
- correlación bajar peso < −0,3,
- correlación ganar músculo > 0,3,
- metas ambiciosas se cumplen menos (29,6 % vs 7,4 %).

## Estructura

```text
analytics/                 API FastAPI que sirve analytics.json
dataset/                   generador y validador del dataset sintético
frontend/                  HTML/JS del dashboard (incluye pestaña Analítica)
haproxy/                   configuración de entrada (stack y compose)
services/                  users, measurements, progress, workouts, goals
spark/                     ETL, KPIs y scripts de ejecución
tests/load/                prueba de carga sin dependencias
docker-stack.yml           despliegue en Swarm
docker-compose.yml         despliegue local para desarrollo
GUIA PARA FITTRACK.md      montaje sin Docker (systemd + nginx)
```

## Problemas conocidos

- **`host not found in upstream` en nginx:** el nginx del stack solo sirve el frontend estático;
  HAProxy es el único entrypoint de `/api/*`. No volver a agregar `proxy_pass` a servicios en
  `frontend/nginx.conf`.
- **Spark con ANSI:** el ETL usa `try_to_date` y `spark.sql.ansi.enabled=false` para tolerar la
  suciedad controlada del dataset.
- **Memoria:** el servidor tiene 3,8 GiB. Los scripts piden 768 MB de driver y 1500 MB de executor.
  Si falla, bajar `EXECUTOR_MEMORY` o detener el stack durante el batch.
- **El worker del cliente no ve los CSV:** copiar el dataset a la misma ruta en el cliente antes de
  agregarlo como worker.
- **Tareas huérfanas `fittrack_nginx`:** restos de un intento anterior; no pertenecen al stack actual.

## Entrega

- Informe IEEE (máximo 10 páginas) y diapositivas: en el repositorio del proyecto.
- Repositorio: `https://github.com/nicocpxmd/fittrack`, rama `proyecto-final`.
