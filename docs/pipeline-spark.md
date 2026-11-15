# Pipeline de Spark: dataset, ETL y KPIs

[<- Volver al README](../README.md)


La aplicación funciona sin Spark usando la muestra que se copia en el [README](../README.md). Si quieres ejecutar el
análisis real:

## Generar el dataset

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

## Ejecutar Spark

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

## Salidas

- `analytics/curated/`: Parquet limpio (`usuarios`, `medidas`, `rutinas`, `metas`).
- `analytics/data/cleaning.json`: conteos de limpieza.
- `analytics/data/analytics.json`: KPIs que consume el dashboard.

El servicio `analytics` monta `analytics/data` en `/data` (solo lectura). Si vuelves a correr Spark,
la API toma el JSON nuevo por `mtime` sin reiniciar el contenedor.

## Resultados de referencia (100.000 usuarios)

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

## Dos workers

El pipeline funciona con un worker. Para dos nodos necesitas que ambos vean el mismo dataset y el
mismo directorio de salida (NFS/HDFS) o copiar el dataset a la misma ruta en cada worker. Con
`file://` local, el Parquet de salida quedaría repartido entre nodos. El laboratorio usa un solo
worker; el modo de dos nodos queda como trabajo futuro.



## Validación del pipeline

El JSON de analítica incluye `validacion` con los patrones sembrados por el generador:

- abandono temprano ≈ 40 %,
- pico de enero ≥ 1,4×,
- correlación bajar peso < −0,3,
- correlación ganar músculo > 0,3,
- metas ambiciosas se cumplen menos (29,6 % vs 7,4 %).

La correspondencia entre el dataset y las tablas de la app está en
[`dataset/CONSISTENCIA.md`](../dataset/CONSISTENCIA.md).


