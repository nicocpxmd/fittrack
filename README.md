# FitTrack — seguimiento físico con analítica sobre un dataset sintético

FitTrack es una aplicación de microservicios (usuarios, medidas, progreso, rutinas y metas) con un
dashboard web. Incluye además un pipeline de Apache Spark que procesa un dataset de 8,4 millones de
filas y publica indicadores agregados en la pestaña **Analítica**, visible solo para administradores.

La aplicación y el análisis están separados a propósito: los microservicios usan sus bases de datos y
el pipeline trabaja por lotes sobre archivos, publicando un JSON que la app solo lee.

Entrega congelada: tag **`v4.0-proyecto-final`**.

## Qué incluye

| Carpeta | Contenido |
|---|---|
| `services/` | Cinco microservicios REST: usuarios, medidas, progreso, rutinas y metas |
| `analytics/` | API de solo lectura de los KPIs (FastAPI) |
| `frontend/` | Dashboard HTML/JS con la pestaña Analítica |
| `haproxy/` | Entrada única y balanceo de `/api/*` |
| `docker/` | Init de MySQL y migraciones de base |
| `spark/` | ETL y cálculo de KPIs |
| `dataset/` | Generador, validador y diccionario del dataset sintético |
| `tests/load/` | Prueba de carga sin dependencias externas |
| `report/`, `slides/` | Informe IEEE y diapositivas |
| `docs/` | Guías detalladas, enlazadas al final |

## Requisitos

- Docker con Compose v2 (Docker Desktop o Docker Engine)
- 4 GB de RAM disponibles
- Git

## Cómo ejecutar

### 1. Clonar

```bash
git clone -b proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
```

> La rama por defecto (`main`) está atrasada hasta que se haga el merge. Usa `proyecto-final` o el tag
> `v4.0-proyecto-final`.

### 2. Crear el `.env`

```bash
cp .env.example .env
```

Edita cuatro valores: `POSTGRES_PASSWORD`, `DB_PASSWORD`, `SECRET_KEY` y `ADMIN_PASSWORD`. Genera las
claves con:

```bash
openssl rand -hex 32   # SECRET_KEY (64 caracteres)
openssl rand -hex 12   # ADMIN_PASSWORD
```

`ADMIN_EMAIL` es la cuenta que verá la analítica; puedes dejar el valor de ejemplo o cambiarlo. Usa
contraseñas alfanuméricas: `@`, `:`, `/`, `?` o `#` pueden romper la `DATABASE_URL` de Postgres.

### 3. Copiar la muestra de analítica

```bash
mkdir -p analytics/data
cp analytics/sample/analytics.json analytics/data/analytics.json
```

Así el dashboard funciona sin correr Spark. Si quieres recalcular con el dataset completo, salta este
paso y sigue el [pipeline de Spark](docs/pipeline-spark.md).

### 4. Levantar

```bash
docker compose up -d --build
docker compose ps
```

La primera vez tarda varios minutos. Espera a los once contenedores en `running` y a las tres bases en
`healthy`.

### 5. Abrir

| Recurso | URL |
|---|---|
| Dashboard | `http://localhost:8080` |
| Stats de HAProxy | `http://localhost:8404` (admin / admin) |

Regístrate desde **Crear cuenta**: verás Medidas, Progreso, Metas y Rutinas, pero **no** la pestaña
Analítica. Cierra sesión y entra con `ADMIN_EMAIL` y `ADMIN_PASSWORD` para verla.

Para detener: `docker compose down`. Para borrar también los datos: `docker compose down -v`.

## Qué deberías ver

- Un usuario normal opera la app, pero la analítica le responde `401` o `403`.
- El administrador ve la pestaña **Analítica** con los indicadores del dataset.
- `curl -s http://localhost:8080/api/analytics/health` responde `"status":"ok"` sin token.

Si algo no cuadra, revisa [problemas comunes](docs/troubleshooting.md) y
[verificación](docs/verificacion.md).

## Modo clúster (opcional)

En el laboratorio se desplegó en Docker Swarm con dos nodos; es el modo que se sustenta.

```bash
docker swarm init
docker node update --label-add role=server <hostname-manager>
docker node update --label-add role=worker <hostname-worker>

set -a; . ./.env; set +a
export FITTRACK_DIR="$PWD"
docker stack deploy -c docker-stack.yml fittrack
```

Detalle de etiquetas, réplicas, imágenes y migración de una base existente:
[despliegue en Swarm](docs/despliegue-swarm.md).

## Pipeline de Spark (opcional)

La app funciona con la muestra sin ejecutar Spark. Para recalcular los KPIs:

```bash
# dataset de prueba (2.000 usuarios)
docker compose --profile tools run --rm dataset generar_dataset.py --salida /data --usuarios 2000 --semilla 42

# ETL + KPIs
docker run --rm -v "$PWD:/work" -w /work --user root --entrypoint bash \
  -e SPARK_HOME=/opt/spark -e ROOT=/work -e MASTER=local[4] \
  apache/spark:4.2.1-python3 spark/run_all.sh
```

Dataset completo, resultados de referencia y validación: [pipeline de Spark](docs/pipeline-spark.md).

## Problemas comunes

| Síntoma | Causa habitual |
|---|---|
| `fe_sendauth: no password supplied` | Se desplegó sin exportar el `.env` |
| 8080 u 8404 ocupados | Otro stack de Compose sigue arriba |
| `analytics` responde 503 | Falta `analytics/data/analytics.json` o `users` no responde |
| 403 en la analítica | El token no es de un administrador |

Los quince casos con su solución: [troubleshooting](docs/troubleshooting.md).

## Documentación

- **Informe IEEE:** [`report/reporte.pdf`](report/reporte.pdf)
- **Diapositivas:** [`slides/slides.md`](slides/slides.md)
- **Dataset:** [`dataset/README.md`](dataset/README.md) y
  [`dataset/CONSISTENCIA.md`](dataset/CONSISTENCIA.md)
- **Configuración y roles:** [variables, puertos y acceso](docs/configuracion.md)
- **Verificación:** [API, carga, estrés y failover](docs/verificacion.md)
- **Estructura del repositorio:** [estructura](docs/estructura.md)
- **Equipo:** [`docs/team-handoff.md`](docs/team-handoff.md)
- **Guía sin Docker (legado):** [`docs/legacy/bare-metal/README.md`](docs/legacy/bare-metal/README.md)
