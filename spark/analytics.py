#!/usr/bin/env python3
"""KPIs de FitTrack sobre el Parquet curado.

Genera un unico JSON con las secciones que consume el dashboard:
dataset, limpieza, KPIs, retencion, adherencia, metas, peso, estacionalidad,
rutinas y ciudades. Tambien deja metricas para validar contra los patrones
sembrados por el generador.

Uso:
  spark-submit spark/analytics.py \
    --curated /root/fittrack/analytics/curated \
    --cleaning /root/fittrack/analytics/data/cleaning.json \
    --out /root/fittrack/analytics/data/analytics.json
"""
import argparse
import datetime
import decimal
import json
import math
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

PESO_MIN_KG = 30.0
PESO_MAX_KG = 250.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--curated", default="/root/fittrack/analytics/curated")
    parser.add_argument("--cleaning", default="/root/fittrack/analytics/data/cleaning.json")
    parser.add_argument("--out", default="/root/fittrack/analytics/data/analytics.json")
    return parser.parse_args()


def jsonable(value):
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value


def records(frame):
    return [{key: jsonable(value) for key, value in row.asDict().items()} for row in frame.collect()]


def scalar(frame, default=None):
    row = frame.first()
    if row is None:
        return default
    value = row[0]
    return jsonable(value)


def main():
    args = parse_args()
    spark = (
        SparkSession.builder.appName("fittrack-analytics")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    users = spark.read.parquet(os.path.join(args.curated, "usuarios"))
    medidas = spark.read.parquet(os.path.join(args.curated, "medidas"))
    rutinas = spark.read.parquet(os.path.join(args.curated, "rutinas"))
    metas = spark.read.parquet(os.path.join(args.curated, "metas"))

    total_users = users.count()

    # ---------------- actividad por usuario ----------------
    rut_act = rutinas.groupBy("user_id").agg(
        F.min("fecha").alias("primera_rutina"),
        F.max("fecha").alias("ultima_rutina"),
        F.count("*").alias("sesiones"),
    )
    med_act = medidas.groupBy("user_id").agg(
        F.min("fecha").alias("primera_medida"),
        F.max("fecha").alias("ultima_medida"),
        F.count("*").alias("medidas"),
    )
    act = (
        users.select("user_id", "fecha_registro", "objetivo_fitness", "ciudad", "genero", "unidad_peso")
        .join(rut_act, "user_id", "left")
        .join(med_act, "user_id", "left")
        .withColumn(
            "primera_actividad",
            F.least(F.col("primera_rutina"), F.col("primera_medida")),
        )
        .withColumn(
            "ultima_actividad",
            F.greatest(F.col("ultima_rutina"), F.col("ultima_medida")),
        )
    )
    act = act.withColumn(
        "semanas_activo",
        F.greatest(
            F.datediff(F.col("ultima_actividad"), F.col("fecha_registro")) / F.lit(7.0),
            F.lit(0.0),
        ),
    )
    act = act.withColumn("sesiones", F.coalesce(F.col("sesiones"), F.lit(0)))
    act = act.withColumn(
        "sesiones_semana",
        F.col("sesiones") / F.greatest(F.col("semanas_activo"), F.lit(1.0)),
    ).cache()

    max_row = act.agg(F.max("ultima_actividad")).first()
    max_actividad = max_row[0] if max_row else None
    activos_12s = act.filter(
        F.col("ultima_actividad").isNotNull()
        & (F.datediff(F.lit(max_actividad), F.col("ultima_actividad")) <= 84)
    ).count()

    retencion = {
        f"despues_{semanas}_semanas": round(
            act.filter(F.col("semanas_activo") >= semanas).count() / total_users, 4
        )
        for semanas in (4, 12, 26)
    }
    cohortes = (
        act.withColumn("cohorte", F.date_format("fecha_registro", "yyyy-MM"))
        .groupBy("cohorte")
        .agg(
            F.count("*").alias("usuarios"),
            F.sum(F.when(F.col("semanas_activo") >= 12, 1).otherwise(0)).alias("activos_12s"),
        )
        .withColumn(
            "retencion_12s",
            F.round(F.col("activos_12s") / F.col("usuarios"), 4),
        )
        .orderBy("cohorte")
    )

    adherencia = (
        act.withColumn(
            "bucket",
            F.when(F.col("sesiones_semana") < 0.5, "0")
            .when(F.col("sesiones_semana") < 1.5, "1")
            .when(F.col("sesiones_semana") < 3.0, "2-3")
            .when(F.col("sesiones_semana") < 5.0, "4-5")
            .otherwise("6+"),
        )
        .groupBy("bucket")
        .count()
        .orderBy("bucket")
    )

    # ---------------- peso ----------------
    valid = medidas.filter(
        F.col("peso_kg").isNotNull()
        & (F.col("peso_kg") >= PESO_MIN_KG)
        & (F.col("peso_kg") <= PESO_MAX_KG)
    )
    primera = (
        valid.withColumn(
            "rn",
            F.row_number().over(
                Window.partitionBy("user_id").orderBy(F.col("fecha").asc(), F.col("medida_id").asc())
            ),
        )
        .filter(F.col("rn") == 1)
        .select(
            "user_id",
            F.col("peso_kg").alias("peso_inicial"),
            F.col("fecha").alias("fecha_inicial"),
        )
    )
    ultima = (
        valid.withColumn(
            "rn",
            F.row_number().over(
                Window.partitionBy("user_id").orderBy(F.col("fecha").desc(), F.col("medida_id").desc())
            ),
        )
        .filter(F.col("rn") == 1)
        .select(
            "user_id",
            F.col("peso_kg").alias("peso_final"),
            F.col("fecha").alias("fecha_final"),
        )
    )
    delta = (
        primera.join(ultima, "user_id")
        .withColumn("dias", F.datediff(F.col("fecha_final"), F.col("fecha_inicial")))
        .filter(F.col("dias") >= 56)
        .withColumn("delta_kg", F.col("peso_final") - F.col("peso_inicial"))
    )
    delta = delta.join(
        act.select("user_id", "objetivo_fitness", "sesiones_semana"), "user_id", "left"
    ).cache()
    peso_por_objetivo = (
        delta.groupBy("objetivo_fitness")
        .agg(
            F.count("*").alias("usuarios"),
            F.round(F.avg("delta_kg"), 2).alias("cambio_promedio_kg"),
            F.round(F.corr("delta_kg", "sesiones_semana"), 3).alias("correlacion_sesiones"),
        )
        .orderBy("objetivo_fitness")
    )
    cambio_promedio = scalar(delta.agg(F.round(F.avg("delta_kg"), 2)).alias("v"))

    # ---------------- metas ----------------
    metas_validas = metas.filter(
        F.col("valor_inicial_norm").isNotNull()
        & (F.col("valor_inicial_norm") != 0)
        & F.col("valor_objetivo_norm").isNotNull()
    ).withColumn(
        "ambicion",
        F.abs(F.col("valor_objetivo_norm") / F.col("valor_inicial_norm") - F.lit(1.0)),
    )
    metas_con_tercil = metas_validas.withColumn(
        "tercil", F.ntile(3).over(Window.partitionBy(F.lit(1)).orderBy("ambicion"))
    )
    metas_por_objetivo = (
        metas_con_tercil.groupBy("objetivo_fitness")
        .agg(
            F.count("*").alias("metas"),
            F.sum(F.when(F.col("estado") == "cumplida", 1).otherwise(0)).alias("cumplidas"),
        )
        .withColumn(
            "tasa_cumplimiento",
            F.round(F.col("cumplidas") / F.col("metas"), 4),
        )
        .orderBy("objetivo_fitness")
    )
    metas_por_ambicion = (
        metas_con_tercil.groupBy("tercil")
        .agg(
            F.count("*").alias("metas"),
            F.sum(F.when(F.col("estado") == "cumplida", 1).otherwise(0)).alias("cumplidas"),
        )
        .withColumn(
            "tasa_cumplimiento",
            F.round(F.col("cumplidas") / F.col("metas"), 4),
        )
        .orderBy("tercil")
    )
    metas_por_estado = metas.groupBy("estado").count().orderBy(F.desc("count"))
    total_metas = metas.count()
    metas_cumplidas = metas.filter(F.col("estado") == "cumplida").count()
    tasa_cumplimiento = round(metas_cumplidas / total_metas, 4) if total_metas else 0.0

    # ---------------- estacionalidad ----------------
    registros_mes = (
        users.groupBy(F.date_format("fecha_registro", "yyyy-MM").alias("mes"))
        .count()
        .orderBy("mes")
    )
    sesiones_mes = (
        rutinas.groupBy(F.date_format("fecha", "yyyy-MM").alias("mes"))
        .count()
        .orderBy("mes")
    )
    registros_mes_lista = records(registros_mes)
    enero = next((r["count"] for r in registros_mes_lista if r["mes"] == "2025-01"), 0)
    otros = [r["count"] for r in registros_mes_lista if r["mes"] != "2025-01"]
    promedio_otros = sum(otros) / len(otros) if otros else 0
    pico_enero = round(enero / promedio_otros, 2) if promedio_otros else 0.0

    # ---------------- rutinas ----------------
    rutinas_por_tipo = (
        rutinas.groupBy("tipo_enfoque")
        .agg(
            F.count("*").alias("sesiones"),
            F.round(F.avg("duracion_min"), 1).alias("duracion_promedio_min"),
            F.round(F.avg("intensidad"), 2).alias("intensidad_promedio"),
        )
        .orderBy(F.desc("sesiones"))
    )
    rutinas_por_grupo = (
        rutinas.groupBy("grupo_muscular")
        .agg(F.count("*").alias("sesiones"))
        .orderBy(F.desc("sesiones"))
    )
    duracion_promedio = scalar(rutinas.agg(F.round(F.avg("duracion_min"), 1)).alias("v"))
    intensidad_promedio = scalar(rutinas.agg(F.round(F.avg("intensidad"), 2)).alias("v"))

    # ---------------- ciudades ----------------
    usuarios_por_ciudad = (
        users.groupBy("ciudad").count().orderBy(F.desc("count"))
    )

    # ---------------- abandono temprano ----------------
    abandono_temprano = act.filter(
        (F.col("semanas_activo") <= 12)
        & (F.col("ultima_actividad").isNotNull())
        & (F.datediff(F.lit(max_actividad), F.col("ultima_actividad")) > 28)
    ).count()
    abandono_pct = round(abandono_temprano / total_users, 4)

    # ---------------- limpieza (del ETL) ----------------
    limpieza = {}
    if os.path.exists(args.cleaning):
        with open(args.cleaning, encoding="utf-8") as handle:
            limpieza = json.load(handle)

    resultado = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "dataset": {
            "usuarios": total_users,
            "medidas": medidas.count(),
            "rutinas": rutinas.count(),
            "metas": total_metas,
            "filas_total": total_users + medidas.count() + rutinas.count() + total_metas,
            "desde": str(scalar(users.agg(F.min("fecha_registro")).alias("v"))),
            "hasta": str(scalar(users.agg(F.max("fecha_registro")).alias("v"))),
        },
        "limpieza": limpieza,
        "kpis": {
            "usuarios": total_users,
            "usuarios_activos_12s": activos_12s,
            "promedio_sesiones_semana": round(
                scalar(act.agg(F.avg("sesiones_semana")).alias("v")) or 0.0, 2
            ),
            "tasa_cumplimiento_metas": tasa_cumplimiento,
            "cambio_promedio_peso_kg": cambio_promedio,
        },
        "retencion": {
            **retencion,
            "por_cohorte": records(cohortes),
        },
        "adherencia": records(adherencia),
        "metas": {
            "por_objetivo": records(metas_por_objetivo),
            "por_ambicion": records(metas_por_ambicion),
            "por_estado": records(metas_por_estado),
        },
        "peso": {
            "por_objetivo": records(peso_por_objetivo),
            "usuarios_con_delta": delta.count(),
        },
        "estacionalidad": {
            "registros_por_mes": registros_mes_lista,
            "sesiones_por_mes": records(sesiones_mes),
            "pico_enero_ratio": pico_enero,
        },
        "rutinas": {
            "por_tipo": records(rutinas_por_tipo),
            "por_grupo_muscular": records(rutinas_por_grupo),
            "duracion_promedio_min": duracion_promedio,
            "intensidad_promedio": intensidad_promedio,
        },
        "ciudades": records(usuarios_por_ciudad),
        "validacion": {
            "abandono_temprano_pct": abandono_pct,
            "pico_enero_ratio": pico_enero,
            "correlacion_bajar_peso": next(
                (
                    row["correlacion_sesiones"]
                    for row in records(peso_por_objetivo)
                    if row["objetivo_fitness"] == "bajar_peso"
                ),
                None,
            ),
            "correlacion_ganar_musculo": next(
                (
                    row["correlacion_sesiones"]
                    for row in records(peso_por_objetivo)
                    if row["objetivo_fitness"] == "ganar_musculo"
                ),
                None,
            ),
        },
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(resultado, handle, indent=2, ensure_ascii=False)
    print(json.dumps(resultado["kpis"], indent=2, ensure_ascii=False))
    print("Escrito:", args.out)

    spark.stop()


if __name__ == "__main__":
    main()
