# Pipeline Spark — parte 2

Convierte el dataset sintético de `dataset/data` en Parquet curado y luego en los KPIs que consume
el dashboard.

## Requisitos

- Spark 4.2.0 en `/root/labSpark/spark-4.2.0-bin-hadoop3`.
- Dataset de 100.000 usuarios ya generado y validado:
  `/root/fittrack/dataset/data` (741 MB, 8.462.080 filas).
- Master y worker arriba:

  ```bash
  cd /root/labSpark/spark-4.2.0-bin-hadoop3/sbin
  ./start-master.sh
  ./start-worker.sh spark://192.168.100.3:7077
  ```

  Comprobar en `http://192.168.100.3:8080`: **Alive Workers: 1** y **Cores in use: 4**.

## Ejecución

Desde `/root/fittrack`:

```bash
bash spark/run_etl.sh
bash spark/run_analytics.sh
```

O los dos:

```bash
bash spark/run_all.sh
```

Variables opcionales:

| Variable | Por defecto |
|---|---|
| `SPARK_HOME` | `/root/labSpark/spark-4.2.0-bin-hadoop3` |
| `MASTER` | `spark://192.168.100.3:7077` |
| `ROOT` | `/root/fittrack` |
| `RAW` | `$ROOT/dataset/data` |
| `CURATED` | `$ROOT/analytics/curated` |
| `OUT` | `$ROOT/analytics/data/analytics.json` |

## Qué hace `etl.py`

1. Lee los cuatro CSV con esquema explícito (todo texto y luego casteo controlado).
2. Limpia:
   - duplicados exactos por `medida_id` y `rutina_id`;
   - fechas ISO y `dd/mm/aaaa` con `coalesce`;
   - pesos en libras → kg con `unidad_peso` del usuario;
   - pesos fuera de 30–250 kg (cero, negativos, multiplicados por 10);
   - conserva nulos de `cintura`, `brazo` y `pecho` para reportarlos.
3. Normaliza metas de peso a kg (`valor_inicial_norm`, `valor_objetivo_norm`).
4. Escribe Parquet en `analytics/curated/`:
   - `usuarios`, `metas`;
   - `medidas` y `rutinas` particionadas por `anio`.
5. Escribe `analytics/data/cleaning.json` con los conteos de limpieza.

## Qué hace `analytics.py`

Lee el Parquet y calcula:

- **KPIs:** usuarios, activos en las últimas 12 semanas, sesiones/semana, cumplimiento de metas,
  cambio promedio de peso.
- **Retención:** a 4, 12 y 26 semanas; por cohorte mensual.
- **Adherencia:** distribución de sesiones/semana.
- **Metas:** cumplimiento por objetivo, por tercil de ambición y por estado.
- **Peso:** cambio promedio y correlación sesiones/semana vs cambio, por objetivo.
- **Estacionalidad:** registros y sesiones por mes; pico de enero.
- **Rutinas:** sesiones por tipo y grupo muscular; duración e intensidad promedio.
- **Ciudades:** usuarios por ciudad.
- **Validación:** abandono temprano, pico de enero y correlaciones contra los patrones sembrados.

Salida: `analytics/data/analytics.json`.

## Memoria

El servidor tiene 3.8 GiB y el stack `fittrack` está corriendo. Los scripts piden 768 MB de driver y
1500 MB de executor por defecto (`DRIVER_MEMORY` y `EXECUTOR_MEMORY`). Si Spark falla por memoria:

1. bajar `--executor-memory` a `1500m` en los scripts;
2. o detener temporalmente el stack (`docker stack rm fittrack`) y volver a desplegarlo al terminar;
3. o usar el worker del cliente (ver abajo).

## Dos nodos (cliente como worker)

El master sigue en `servidorUbuntu`. En `clienteUbuntu`:

1. Instalar/copiar Spark 4.2.0 en la misma ruta.
2. Copiar el dataset a la misma ruta (`/root/fittrack/dataset/data`) para que el worker pueda leerlo.
3. Arrancar el worker apuntando al master:

   ```bash
   /root/labSpark/spark-4.2.0-bin-hadoop3/sbin/start-worker.sh spark://192.168.100.3:7077
   ```

4. Verificar en la UI del master que hay **2 workers**.
5. Ejecutar `spark/run_all.sh` y comparar tiempos con 1 vs 2 workers.

## Problemas conocidos

- **Connection refused** al master: no está corriendo; arrancarlo.
- **OutOfMemory**: reducir memoria o parar el stack durante el batch.
- **El worker del cliente no encuentra los CSV**: falta copiar el dataset a la misma ruta.
- **Parquet con permisos**: Spark corre como root; `analytics/curated` y `analytics/data` deben ser
  escribibles por root.
