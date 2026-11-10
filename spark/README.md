# Pipeline Spark — parte 2

Convierte el dataset sintético de `dataset/data` en Parquet curado y luego en los KPIs que consume
el dashboard.

## Requisitos

- Dataset generado en `dataset/data` (ver `dataset/README.md`).
- Spark 4.2.x, o la imagen Docker `apache/spark:4.2.1-python3`.
- Python 3.10+ solo si ejecutas Spark instalado en el host.
- Para el modo clúster: master y worker de Spark en la misma red.

Los scripts `run_*.sh` detectan la raíz del repositorio desde su propia ubicación. No asumen
`/root/fittrack` ni una IP fija.

## Variables

| Variable | Por defecto | Uso |
|---|---|---|
| `SPARK_HOME` | — | ruta de Spark si no está en `PATH` |
| `SPARK_SUBMIT` | `spark-submit` | binario explícito |
| `MASTER` | `local[*]` | `local[4]` o `spark://<server>:7077` |
| `ROOT` | raíz del repo | ruta del proyecto |
| `RAW` | `$ROOT/dataset/data` | CSV crudos |
| `CURATED` | `$ROOT/analytics/curated` | Parquet de salida |
| `OUT` | `$ROOT/analytics/data/analytics.json` | KPIs |
| `DRIVER_MEMORY` | `768m` | memoria del driver |
| `EXECUTOR_MEMORY` | `1500m` | memoria del executor (clúster) |

## Opción A — Docker (local)

```bash
docker run --rm -v "$PWD:/work" -w /work --user root --entrypoint bash \
  -e SPARK_HOME=/opt/spark -e ROOT=/work -e MASTER=local[4] \
  apache/spark:4.2.1-python3 spark/run_all.sh
```

En PowerShell usa `-v "${PWD}:/work"`. El laboratorio usa Spark 4.2.0; la imagen oficial publica
4.2.1, compatible con la serie 4.2.x.

## Opción B — Spark instalado en el host

```bash
export SPARK_HOME="$HOME/spark-4.2.1-bin-hadoop3"
export PATH="$SPARK_HOME/bin:$PATH"
MASTER=local[4] bash spark/run_all.sh
```

Si ya tienes Spark 4.2.0, apunta `SPARK_HOME` a esa instalación.

## Opción C — Clúster Spark

```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-worker.sh spark://<server-ip>:7077
MASTER=spark://<server-ip>:7077 bash spark/run_all.sh
```

Comprueba la UI en `http://<server-ip>:8080`: debe decir **Alive Workers** y los cores disponibles.

### Dos workers

Para dos nodos, ambos workers deben ver el mismo `dataset/data` y escribir en el mismo `CURATED` y
`OUT` (NFS/HDFS), o copiar el dataset a la misma ruta en cada worker. Con `file://` local, el Parquet
de salida quedaría repartido entre nodos. El laboratorio usa un solo worker; dos nodos es trabajo
futuro.

## Uso

```bash
# ETL + KPIs
bash spark/run_all.sh

# Solo ETL
bash spark/run_etl.sh

# Solo KPIs
bash spark/run_analytics.sh
```

Salidas:

- `analytics/curated/`: Parquet (`usuarios`, `medidas`, `rutinas`, `metas`).
- `analytics/data/cleaning.json`: conteos de limpieza.
- `analytics/data/analytics.json`: KPIs del dashboard.

## Qué hace `etl.py`

1. Lee los cuatro CSV con esquema explícito.
2. Limpia duplicados, fechas `dd/mm/aaaa`, pesos en libras y pesos inválidos (30–250 kg).
3. Normaliza metas de peso a kg.
4. Escribe Parquet particionado por año.
5. Genera `cleaning.json`.

## Qué hace `analytics.py`

1. Lee el Parquet curado.
2. Calcula KPIs: retención, adherencia, metas, peso, estacionalidad, rutinas y ciudades.
3. Compara contra los patrones sembrados por el generador (abandono, pico de enero, correlaciones,
   ambición de metas).
4. Escribe `analytics.json`.

## Problemas conocidos

- **`spark-submit` no encontrado:** define `SPARK_HOME` o agrega `$SPARK_HOME/bin` al `PATH`.
- **Connection refused al master:** el master no está corriendo o `MASTER` apunta a otra IP.
- **OutOfMemory:** baja `EXECUTOR_MEMORY` o detén la aplicación mientras corre el batch.
- **El worker no ve los CSV:** copia el dataset a la misma ruta en cada worker o usa un filesystem
  compartido.
- **Permisos en Docker:** usa `--user root`; el contenedor necesita escribir en `analytics/`.
- **ANSI y fechas:** el ETL usa `try_to_date` y `spark.sql.ansi.enabled=false`; no los cambies sin
  revisar el ETL.
