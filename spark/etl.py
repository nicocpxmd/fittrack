#!/usr/bin/env python3
"""ETL de FitTrack-Synth: CSV crudos -> Parquet curado + reporte de limpieza.

Limpia lo que el generador ensucio a proposito:
  - duplicados exactos por id,
  - fechas en dd/mm/aaaa,
  - pesos en libras (se normalizan a kg),
  - pesos absurdos (0, negativos o multiplicados por 10),
  - nulos en cintura/brazo/pecho (se conservan como null).

Uso:
  spark-submit spark/etl.py \
    --raw /root/fittrack/dataset/data \
    --curated /root/fittrack/analytics/curated \
    --report /root/fittrack/analytics/data/cleaning.json
"""
import argparse
import json
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

LB = 2.20462
PESO_MIN_KG = 30.0
PESO_MAX_KG = 250.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="/root/fittrack/dataset/data")
    parser.add_argument("--curated", default="/root/fittrack/analytics/curated")
    parser.add_argument("--report", default="/root/fittrack/analytics/data/cleaning.json")
    return parser.parse_args()


def read_csv(spark, path, columns):
    schema = T.StructType([T.StructField(name, T.StringType(), True) for name in columns])
    return (
        spark.read.option("header", True)
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .csv(path)
    )


def fecha_col(name):
    """Acepta ISO (aaaa-mm-dd) y dd/mm/aaaa; devuelve una fecha."""
    return F.coalesce(
        F.try_to_date(F.col(name), "yyyy-MM-dd"),
        F.try_to_date(F.col(name), "dd/MM/yyyy"),
    )


def main():
    args = parse_args()
    spark = (
        SparkSession.builder.appName("fittrack-etl")
        .config("spark.sql.shuffle.partitions", "8")
        # El dataset trae suciedad controlada: preferimos null a excepcion.
        .config("spark.sql.ansi.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    raw = args.raw
    curated = args.curated
    os.makedirs(curated, exist_ok=True)
    os.makedirs(os.path.dirname(args.report), exist_ok=True)

    # ---------------- usuarios ----------------
    users = read_csv(
        spark,
        os.path.join(raw, "usuarios.csv"),
        [
            "user_id", "email", "fecha_nacimiento", "genero", "ciudad",
            "altura_cm", "fecha_registro", "objetivo_fitness", "unidad_peso",
        ],
    )
    users = (
        users.withColumn("altura_cm", F.col("altura_cm").cast("double"))
        .withColumn("fecha_nacimiento", fecha_col("fecha_nacimiento"))
        .withColumn("fecha_registro", fecha_col("fecha_registro"))
    )

    # ---------------- medidas ----------------
    medidas_raw = read_csv(
        spark,
        os.path.join(raw, "medidas.csv"),
        ["medida_id", "user_id", "fecha", "peso", "cintura", "brazo", "pecho"],
    )
    total_medidas = medidas_raw.count()
    medidas_raw = medidas_raw.withColumn("medida_id", F.col("medida_id").cast("long"))
    duplicados_medidas = total_medidas - medidas_raw.select("medida_id").distinct().count()
    medidas = medidas_raw.dropDuplicates(["medida_id"])

    medidas = (
        medidas.withColumn("fecha_iso", F.try_to_date(F.col("fecha"), "yyyy-MM-dd"))
        .withColumn("fecha_alt", F.try_to_date(F.col("fecha"), "dd/MM/yyyy"))
        .withColumn("fecha", F.coalesce(F.col("fecha_iso"), F.col("fecha_alt")))
        .withColumn("peso_raw", F.col("peso").cast("double"))
        .withColumn("cintura", F.col("cintura").cast("double"))
        .withColumn("brazo", F.col("brazo").cast("double"))
        .withColumn("pecho", F.col("pecho").cast("double"))
    )
    fechas_otro_formato_medidas = medidas.filter(
        F.col("fecha_iso").isNull() & F.col("fecha_alt").isNotNull()
    ).count()
    nulos = {
        "cintura": medidas.filter(F.col("cintura").isNull()).count(),
        "brazo": medidas.filter(F.col("brazo").isNull()).count(),
        "pecho": medidas.filter(F.col("pecho").isNull()).count(),
    }

    medidas = medidas.join(
        users.select("user_id", "unidad_peso"), on="user_id", how="left"
    ).withColumn(
        "peso_kg",
        F.when(F.col("unidad_peso") == "lb", F.col("peso_raw") / F.lit(LB))
        .otherwise(F.col("peso_raw")),
    )
    invalidos = medidas.filter(
        F.col("peso_kg").isNull()
        | (F.col("peso_kg") < PESO_MIN_KG)
        | (F.col("peso_kg") > PESO_MAX_KG)
    ).count()
    medidas = medidas.filter(
        F.col("peso_kg").isNotNull()
        & (F.col("peso_kg") >= PESO_MIN_KG)
        & (F.col("peso_kg") <= PESO_MAX_KG)
    )
    medidas = medidas.withColumn("anio", F.year("fecha"))

    # ---------------- rutinas ----------------
    rutinas_raw = read_csv(
        spark,
        os.path.join(raw, "rutinas.csv"),
        [
            "rutina_id", "user_id", "fecha", "nombre", "tipo_enfoque",
            "grupo_muscular", "duracion_min", "num_ejercicios", "intensidad",
        ],
    )
    total_rutinas = rutinas_raw.count()
    rutinas_raw = rutinas_raw.withColumn("rutina_id", F.col("rutina_id").cast("long"))
    duplicados_rutinas = total_rutinas - rutinas_raw.select("rutina_id").distinct().count()
    rutinas = rutinas_raw.dropDuplicates(["rutina_id"])
    rutinas = (
        rutinas.withColumn("fecha_iso", F.try_to_date(F.col("fecha"), "yyyy-MM-dd"))
        .withColumn("fecha_alt", F.try_to_date(F.col("fecha"), "dd/MM/yyyy"))
        .withColumn("fecha", F.coalesce(F.col("fecha_iso"), F.col("fecha_alt")))
        .withColumn("duracion_min", F.col("duracion_min").cast("int"))
        .withColumn("num_ejercicios", F.col("num_ejercicios").cast("int"))
        .withColumn("intensidad", F.col("intensidad").cast("int"))
    )
    fechas_otro_formato_rutinas = rutinas.filter(
        F.col("fecha_iso").isNull() & F.col("fecha_alt").isNotNull()
    ).count()

    # ---------------- metas ----------------
    metas = read_csv(
        spark,
        os.path.join(raw, "metas.csv"),
        [
            "meta_id", "user_id", "tipo_medida", "valor_inicial", "valor_objetivo",
            "direccion", "fecha_creacion", "fecha_limite", "estado",
        ],
    )
    metas = (
        metas.withColumn("meta_id", F.col("meta_id").cast("long"))
        .withColumn("valor_inicial", F.col("valor_inicial").cast("double"))
        .withColumn("valor_objetivo", F.col("valor_objetivo").cast("double"))
        .withColumn("fecha_creacion", fecha_col("fecha_creacion"))
        .withColumn("fecha_limite", fecha_col("fecha_limite"))
    )
    metas = metas.join(
        users.select("user_id", "unidad_peso", "objetivo_fitness"),
        on="user_id",
        how="left",
    )
    metas = (
        metas.withColumn(
            "factor_peso",
            F.when(
                (F.col("tipo_medida") == "peso") & (F.col("unidad_peso") == "lb"),
                F.lit(LB),
            ).otherwise(F.lit(1.0)),
        )
        .withColumn("valor_inicial_norm", F.col("valor_inicial") / F.col("factor_peso"))
        .withColumn("valor_objetivo_norm", F.col("valor_objetivo") / F.col("factor_peso"))
    )

    # ---------------- escribir Parquet curado ----------------
    users.write.mode("overwrite").parquet(os.path.join(curated, "usuarios"))
    medidas.write.mode("overwrite").partitionBy("anio").parquet(
        os.path.join(curated, "medidas")
    )
    rutinas.write.mode("overwrite").partitionBy("anio").parquet(
        os.path.join(curated, "rutinas")
    )
    metas.write.mode("overwrite").parquet(os.path.join(curated, "metas"))

    reporte = {
        "fuente": raw,
        "curado": curated,
        "usuarios": users.count(),
        "usuarios_lb": users.filter(F.col("unidad_peso") == "lb").count(),
        "medidas": {
            "filas_originales": total_medidas,
            "duplicados_eliminados": duplicados_medidas,
            "invalidos_eliminados": invalidos,
            "filas_curadas": medidas.count(),
            "fechas_otro_formato": fechas_otro_formato_medidas,
            "nulos": nulos,
        },
        "rutinas": {
            "filas_originales": total_rutinas,
            "duplicados_eliminados": duplicados_rutinas,
            "filas_curadas": rutinas.count(),
            "fechas_otro_formato": fechas_otro_formato_rutinas,
        },
        "metas": {"filas_curadas": metas.count()},
    }
    with open(args.report, "w", encoding="utf-8") as handle:
        json.dump(reporte, handle, indent=2, ensure_ascii=False)
    print(json.dumps(reporte, indent=2, ensure_ascii=False))

    spark.stop()


if __name__ == "__main__":
    main()
