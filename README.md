# FitTrack — Proyecto final de Infraestructura

Aplicación de seguimiento físico basada en microservicios, con dashboard web y un pipeline de
análisis de datos con Apache Spark que alimenta la pestaña **Analítica**.

El proyecto se puede ejecutar de dos formas:

- **Docker Compose (recomendado para reproducir en una máquina):** levanta toda la aplicación, las
  bases de datos y el dashboard con un solo comando. No requiere clúster ni Spark para ver la app.
- **Docker Swarm (modo clúster del curso):** dos nodos, balanceo con HAProxy y escalado de réplicas.
  Es la ruta que cumple el requisito de “clúster de contenedores” del enunciado.

> El enunciado exige un **clúster de contenedores** y un **clúster de procesamiento distribuido**;
> no impone Compose ni Swarm. Compose se usa para que cualquiera pueda reproducir la aplicación en
> su computador; Swarm es el modo clúster que se evalúa y se documenta en el informe.

> El dataset es **sintético y reproducible** (semilla 42), autorizado por el profesor. No contiene
> datos de personas reales.

## Índice

1. [Qué incluye](#1-qué-incluye)
2. [Arquitectura](#2-arquitectura)
3. [Requisitos](#3-requisitos)
4. [Quick start con Docker Compose](#4-quick-start-con-docker-compose)
5. [Pipeline completo con Spark](#5-pipeline-completo-con-spark)
6. [Modo clúster con Docker Swarm](#6-modo-clúster-con-docker-swarm)
7. [Configuración](#7-configuración)
8. [Verificación](#8-verificación)
9. [Pruebas](#9-pruebas)
10. [Troubleshooting](#10-troubleshooting)
11. [Estructura del repositorio](#11-estructura-del-repositorio)
12. [Documentación y entrega](#12-documentación-y-entrega)

## 1. Qué incluye

| Componente | Función |
|---|---|
| `services/users` | Registro, login JWT y perfil (Postgres) |
| `services/measurements` | Medidas corporales (Mongo) |
| `services/progress` | Cálculo de progreso entre fechas (Mongo) |
| `services/workouts` | Rutinas de entrenamiento (MySQL) |
| `services/goals` | Metas y porcentaje de cumplimiento (MySQL) |
| `analytics/` | API de solo lectura que publica los KPIs de Spark |
| `frontend/` | Dashboard HTML/JS con la pestaña **Analítica** |
| `haproxy/` | Entrada única y balanceo de `/api/*` |
| `spark/` | ETL, KPIs y scripts de ejecución |
| `dataset/` | Generador, validador y diccionario del dataset sintético |
| `tests/load/` | Prueba de carga sin dependencias externas |
| `report/`, `slides/` | Informe IEEE y diapositivas de la sustentación |

## 2. Arquitectura

### Docker Compose (una máquina)

```text
Navegador
   │  http://localhost:8080
   ▼
HAProxy (contenedor) ── /api/* ──► users, measurements, progress, goals, workouts, analytics
   │                                   │
   └── / ──► nginx (frontend)          ├── Postgres
                                       ├── Mongo
                                       ├── MySQL
                                       └── analytics/data/analytics.json
```

Todo corre en una sola máquina. Es la forma más simple de ver la aplicación y el dashboard.

### Docker Swarm (dos nodos)

```text
Navegador
   │  http://<worker-ip>:8080
   ▼
HAProxy (worker) ── /api/* ──► servicios (server)
   │
   └── / ──► nginx (worker)   ├── Postgres / Mongo / MySQL (server)
                              └── analytics (server)

Spark (server): dataset → ETL → Parquet → analytics.json → API → dashboard
```

Los servicios con estado y `analytics` se fijan al nodo con `role=server`; nginx y HAProxy al nodo
con `role=worker`. El stack usa labels, no hostnames, para que sea portable.

## 3. Requisitos

- **Git**.
- **Docker Engine 24+** o **Docker Desktop** con **Docker Compose v2**.
- **8 GB de RAM** recomendados (4 GB mínimos para la app; Spark necesita más).
- **3 GB de disco** para imágenes + **741 MB** para el dataset completo.
- Puertos **8080** y **8404** libres.
- Linux, macOS o Windows con Docker Desktop/WSL2. Probado en Ubuntu 22.04 x86_64.
- Opcional para el pipeline: **Spark 4.2.x** instalado o la imagen Docker
  `apache/spark:4.2.1-python3`.
- Opcional para el clúster: **dos hosts Ubuntu 22.04** con Docker y la misma red.

No necesitas Python ni Node en el host: la aplicación corre en contenedores. Solo necesitas Python
si vas a ejecutar la prueba de carga.

## 4. Quick start con Docker Compose

### 4.1 Clonar

```bash
git clone -b proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
```

> La rama por defecto del repositorio es `main`, que todavía está atrasada. Hasta que se haga el
> merge, usa siempre `-b proyecto-final` (o el tag de entrega que se indique).

### 4.2 Crear el `.env`

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Edita `.env`:

| Variable | Qué poner |
|---|---|
| `POSTGRES_PASSWORD` | contraseña de Postgres |
| `DB_PASSWORD` | contraseña root de MySQL |
| `SECRET_KEY` | cadena aleatoria de 64 caracteres hex |

Generar `SECRET_KEY`:

```bash
openssl rand -hex 32
```

En PowerShell:

```powershell
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
```

> Usa contraseñas **alfanuméricas**. Caracteres como `@`, `:`, `/`, `?` o `#` pueden romper la
> `DATABASE_URL` de Postgres.

### 4.3 Cargar una muestra de analítica (recomendado)

El dashboard necesita `analytics/data/analytics.json`. Para ver la pestaña **Analítica** sin correr
Spark, usa la muestra incluida:

```bash
mkdir -p analytics/data
cp analytics/sample/analytics.json analytics/data/analytics.json
```

En PowerShell:

```powershell
New-Item -ItemType Directory -Force analytics/data
Copy-Item analytics/sample/analytics.json analytics/data/analytics.json
```

Si quieres recalcular los KPIs con Spark, salta este paso y sigue la sección 5.

### 4.4 Levantar

```bash
docker compose up -d --build
docker compose ps
```

La primera vez descarga imágenes y construye los servicios; puede tardar varios minutos. Espera a
que `users`, `measurements`, `progress`, `workouts`, `goals`, `analytics` y `haproxy` estén
`running`/`healthy`.

### 4.5 Abrir

| Recurso | URL |
|---|---|
| Dashboard | `http://localhost:8080` |
| API de analítica | `http://localhost:8080/api/analytics/health` |
| Stats de HAProxy | `http://localhost:8404` (admin / admin) |

Registra un usuario desde la pantalla de **Crear cuenta**. No hay una cuenta de prueba publicada:
cada persona crea la suya.

### 4.6 Detener

```bash
docker compose down
```

Para borrar también los datos de las bases (irreversible):

```bash
docker compose down -v
```

## 5. Pipeline completo con Spark

La aplicación funciona sin Spark usando la muestra de la sección 4.3. Si quieres ejecutar el
análisis real:

### 5.1 Generar el dataset

Con el perfil `tools` de Compose (no arranca con `up`):

```bash
# Prueba rápida: 2.000 usuarios (~15 MB)
docker compose --profile tools run --rm dataset generar_dataset.py --salida /data --usuarios 2000 --semilla 42

# Validar
docker compose --profile tools run --rm dataset validar_dataset.py --dir /data
```

Para la corrida completa:

```bash
docker compose --profile tools run --rm dataset generar_dataset.py --salida /data --usuarios 100000 --semilla 42
```

Debe terminar con **24 chequeos OK, 0 con falla**. El dataset completo ocupa ~741 MB en
`dataset/data/` (ignorado por Git).

### 5.2 Ejecutar Spark

**Opción A — Docker (recomendada para local, multiplataforma):**

```bash
docker run --rm -v "$PWD:/work" -w /work --user root --entrypoint bash \
  -e SPARK_HOME=/opt/spark -e ROOT=/work -e MASTER=local[4] \
  apache/spark:4.2.1-python3 spark/run_all.sh
```

En PowerShell cambia `"$PWD:/work"` por `"${PWD}:/work"`.

> La imagen oficial publica Spark **4.2.1**; el laboratorio usa **4.2.0**. El código es compatible
> con la serie 4.2.x. Si necesitas exactamente 4.2.0, usa la opción B.

**Opción B — Spark instalado en el host:**

```bash
export SPARK_HOME="$HOME/spark-4.2.1-bin-hadoop3"
export PATH="$SPARK_HOME/bin:$PATH"
MASTER=local[4] bash spark/run_all.sh
```

**Opción C — clúster Spark del laboratorio:**

```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-worker.sh spark://<server-ip>:7077
MASTER=spark://<server-ip>:7077 bash spark/run_all.sh
```

### 5.3 Salidas

- `analytics/curated/`: Parquet limpio (`usuarios`, `medidas`, `rutinas`, `metas`).
- `analytics/data/cleaning.json`: conteos de limpieza.
- `analytics/data/analytics.json`: KPIs que consume el dashboard.

El servicio `analytics` monta `analytics/data` en `/data` (solo lectura). Si vuelves a correr Spark,
la API toma el JSON nuevo por `mtime` sin reiniciar el contenedor.

### 5.4 Resultados de referencia (100.000 usuarios)

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

### 5.5 Dos workers

El pipeline funciona con un worker. Para dos nodos necesitas que ambos vean el mismo dataset y el
mismo directorio de salida (NFS/HDFS) o copiar el dataset a la misma ruta en cada worker. Con
`file://` local, el Parquet de salida quedaría repartido entre nodos. El laboratorio usa un solo
worker; el modo de dos nodos queda como trabajo futuro.

## 6. Modo clúster con Docker Swarm

Esta es la ruta que cumple el requisito de clúster del enunciado. Requiere dos hosts Linux con
Docker.

### 6.1 Inicializar el Swarm

En el nodo que será manager:

```bash
docker swarm init --advertise-addr <server-ip>
```

Copia el comando `docker swarm join --token ...` que imprime y ejecútalo en el worker:

```bash
docker swarm join --token <token> <server-ip>:2377
```

Verifica:

```bash
docker node ls
```

### 6.2 Etiquetar los nodos

El stack usa labels, no hostnames:

```bash
docker node update --label-add role=server <hostname-del-manager>
docker node update --label-add role=worker <hostname-del-worker>
```

Si un nodo tiene las dos funciones, puedes ponerle ambos labels; pero el stack espera al menos un
nodo `role=server` y uno `role=worker`.

### 6.3 Repositorio y ruta

Clona el repo en el nodo **server** (en el laboratorio, el manager). El stack usa
`${FITTRACK_DIR:-/root/fittrack}` para los bind mounts de MySQL y `analytics`:

```bash
cd /ruta/al/fittrack
export FITTRACK_DIR="$PWD"
```

Si el repo está en `/root/fittrack`, no hace falta exportar nada: es el valor por defecto.

### 6.4 Imágenes

El stack usa las imágenes publicadas `nicocpxm/fittrack-*`. Si no tienes acceso o cambiaste código,
construye y publica en **tu** namespace y actualiza los `image:` del stack:

```bash
docker build -t <tu-usuario>/fittrack-nginx:v4 ./frontend
docker build -t <tu-usuario>/fittrack-haproxy:v2 ./haproxy
docker build -t <tu-usuario>/fittrack-analytics:v1 ./analytics
docker push <tu-usuario>/fittrack-nginx:v4
docker push <tu-usuario>/fittrack-haproxy:v2
docker push <tu-usuario>/fittrack-analytics:v1
```

Los servicios `users`, `measurements`, `progress`, `workouts` y `goals` también tienen imágenes
publicadas; si las reconstruyes, actualiza sus tags.

### 6.5 Desplegar

```bash
set -a
. ./.env
set +a
export FITTRACK_DIR="${FITTRACK_DIR:-$PWD}"
docker stack deploy -c docker-stack.yml fittrack
docker stack services fittrack
```

Espera a que todos los servicios estén `1/1`. El entrypoint es `http://<worker-ip>:8080`; las stats
de HAProxy, `http://<worker-ip>:8404` (admin / admin).

### 6.6 Escalar

```bash
docker service scale fittrack_users=3 fittrack_measurements=3
docker stack services fittrack
```

Las réplicas de servicios sin estado pueden repartirse entre los nodos según los labels y la
disponibilidad. Los servicios con estado permanecen en `role=server`.

### 6.7 Notas del laboratorio

El laboratorio del curso usó dos VMs (una manager y una worker) y un servidor Spark local. Esa
configuración específica está documentada en el repo de infraestructura del curso. Este README usa
placeholders para que funcione en cualquier entorno; si usas el laboratorio, reemplaza
`<server-ip>` y `<worker-ip>` por las IPs de tus VMs y etiqueta los nodos como se indica.

## 7. Configuración

### 7.1 Variables del stack

| Variable | Uso |
|---|---|
| `POSTGRES_PASSWORD` | contraseña de Postgres (users) |
| `DB_PASSWORD` | contraseña root de MySQL (workouts, goals) |
| `SECRET_KEY` | firma de los JWT |
| `FITTRACK_DIR` | ruta del repo en el nodo server (solo Swarm) |

`.env` no se versiona. `.env.example` tiene valores de ejemplo.

### 7.2 Puertos

| Puerto | Servicio |
|---|---|
| `8080` | HAProxy / dashboard |
| `8404` | stats de HAProxy |
| `5432`, `27017`, `3306` | bases de datos (solo red interna) |
| `8001`–`8006` | servicios (solo red interna) |

### 7.3 Variables de Spark

| Variable | Por defecto | Uso |
|---|---|---|
| `SPARK_HOME` | — | ruta de Spark si no está en `PATH` |
| `SPARK_SUBMIT` | `spark-submit` | binario explícito |
| `MASTER` | `local[*]` | `local[4]` o `spark://<server>:7077` |
| `ROOT` | raíz del repo | ruta del proyecto |
| `DRIVER_MEMORY` | `768m` | memoria del driver |
| `EXECUTOR_MEMORY` | `1500m` | memoria del executor (modo clúster) |

Los scripts `spark/run_*.sh` detectan la raíz del repo automáticamente y aceptan estas variables.

## 8. Verificación

### 8.1 Contenedores

```bash
docker compose ps
# o, en Swarm:
docker stack services fittrack
```

### 8.2 API y dashboard

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/
curl -s http://localhost:8080/api/analytics/health
curl -s http://localhost:8080/api/analytics/kpis
curl -s -o /dev/null -w "%{http_code}\n" -u admin:admin http://localhost:8404/
```

Esperado: `200`, un JSON con `"status":"ok"` y los KPIs, y `200` en las stats.

> En Swarm, reemplaza `localhost` por `<worker-ip>` en estos comandos.

### 8.3 Dataset

```bash
docker compose --profile tools run --rm dataset validar_dataset.py --dir /data
```

Esperado: **24 chequeos OK, 0 con falla**.

### 8.4 Prueba de carga

```bash
python tests/load/load_test.py \
  --base http://localhost:8080 \
  --email demo@tudominio.com \
  --password 'ChangeMe123' \
  --requests 500 --concurrency 20
```

El script registra el usuario si no existe. Usa un correo de un dominio válido (el validador rechaza
dominios reservados como `.test`). No uses una cuenta real.

Resultados de referencia:

| Réplicas | RPS | p50 | p95 | Errores |
|---|---|---|---|---|
| 1 | 38,15 | 513,09 ms | 654,58 ms | 0 |
| 3 | **72,05** | **272,48 ms** | **411,70 ms** | 0 |

## 9. Validación del pipeline

El JSON de analítica incluye `validacion` con los patrones sembrados por el generador:

- abandono temprano ≈ 40 %,
- pico de enero ≥ 1,4×,
- correlación bajar peso < −0,3,
- correlación ganar músculo > 0,3,
- metas ambiciosas se cumplen menos (29,6 % vs 7,4 %).

La correspondencia entre el dataset y las tablas de la app está en
[`dataset/CONSISTENCIA.md`](dataset/CONSISTENCIA.md).

## 10. Troubleshooting

### El puerto 8080 o 8404 está ocupado

Cambia el mapeo en `docker-compose.yml` (`"8080:80"`, `"8404:8404"`) o detén el proceso que los usa.

### `analytics` responde 503

Falta `analytics/data/analytics.json`. Copia la muestra de la sección 4.3 o corre Spark (sección 5).

### Las bases no arrancan o los esquemas no están

La primera inicialización de MySQL/Postgres tarda. Revisa:

```bash
docker compose logs mysql
docker compose logs users
```

Si el volumen se creó antes de tener los esquemas, el init no vuelve a correr. Para reiniciar desde
cero (borra datos):

```bash
docker compose down -v
docker compose up -d --build
```

### Spark no encuentra `spark-submit`

Instala Spark y define `SPARK_HOME`, o usa la imagen Docker de la sección 5.2. Si usas el host:

```bash
export SPARK_HOME="$HOME/spark-4.2.1-bin-hadoop3"
export PATH="$SPARK_HOME/bin:$PATH"
```

### Spark falla por memoria

El servidor de laboratorio tiene 3,8 GiB. Baja `EXECUTOR_MEMORY` o detén el stack mientras corre el
batch. En una máquina de 8 GB o más no debería ser problema.

### La imagen Docker de Spark no puede escribir

Usa `--user root` y `--entrypoint bash` como en la sección 5.2. El contenedor necesita escribir
`analytics/curated` y `analytics/data`.

### Windows: error con la ruta del volumen

En PowerShell usa `"${PWD}:/work"`; en bash, `"$PWD:/work"`. Docker Desktop debe tener habilitado el
acceso a la unidad del proyecto.

### Apple Silicon

El proyecto está probado en x86_64. `mongo:4.4` puede no tener imagen arm64; en un Mac ARM usa un
host x86_64, una VM Linux o ajusta la imagen de Mongo (no probado).

### `host not found in upstream` en nginx

El nginx del stack solo sirve el frontend estático; HAProxy es el único entrypoint de `/api/*`. No
vuelvas a agregar `proxy_pass` a servicios en `frontend/nginx.conf`.

### Spark y fechas `dd/mm/aaaa`

El ETL usa `try_to_date` y `spark.sql.ansi.enabled=false` para tolerar la suciedad controlada. No
cambies esas opciones sin revisar el ETL.

### Reset completo

```bash
# Compose: conserva volúmenes
docker compose down

# Compose: borra datos (irreversible)
docker compose down -v

# Swarm
docker stack rm fittrack
```

## 11. Estructura del repositorio

```text
analytics/                 API FastAPI + muestra de analítica
  main.py
  sample/analytics.json
dataset/                   generador, validador, diccionario y consistencia
frontend/                  HTML/JS del dashboard (incluye pestaña Analítica)
haproxy/                   configuración de entrada (stack y compose)
services/                  users, measurements, progress, workouts, goals
spark/                     ETL, KPIs y scripts de ejecución
tests/load/                prueba de carga sin dependencias
report/                    informe IEEE, figuras y PDF
slides/                    diapositivas de la sustentación
docs/
  team-handoff.md          estado y tareas del equipo
  api-contracts/           contratos de API
  legacy/bare-metal/       guía y deploy del montaje sin Docker (histórico)
docker-compose.yml         ejecución local en una máquina
docker-stack.yml           despliegue en Swarm
.env.example               variables de ejemplo
```

Directorios generados e ignorados por Git:

- `dataset/data/` (CSV del dataset)
- `analytics/curated/` (Parquet)
- `analytics/data/` (JSON de KPIs)
- `tests/load/*.json` (resultados de carga)

## 12. Documentación y entrega

- **README:** esta guía; es la fuente de verdad para instalar y ejecutar.
- **Equipo:** [`docs/team-handoff.md`](docs/team-handoff.md) (estado, tareas y enlaces).
- **Dataset:** [`dataset/README.md`](dataset/README.md) y
  [`dataset/CONSISTENCIA.md`](dataset/CONSISTENCIA.md).
- **Informe IEEE:** [`report/reporte.pdf`](report/reporte.pdf) y
  [`report/reporte.tex`](report/reporte.tex).
- **Diapositivas:** [`slides/slides.md`](slides/slides.md).
- **Legado sin Docker:** [`docs/legacy/bare-metal/README.md`](docs/legacy/bare-metal/README.md).

### Prueba de aceptación

Una persona con Docker debe poder:

1. Clonar el repo en una carpeta limpia.
2. Crear `.env`, copiar la muestra de analítica y ejecutar `docker compose up -d --build`.
3. Abrir `http://localhost:8080`, registrarse y ver la pestaña **Analítica**.
4. Opcional: generar un dataset pequeño y correr Spark en modo local.
5. Si algo falla, encontrar la causa en este README o en el troubleshooting.

Si un paso no se cumple, el README debe corregirse antes de la entrega.
