#!/usr/bin/env bash
# Calcula los KPIs del dashboard a partir del Parquet curado.
set -euo pipefail

SPARK_HOME="${SPARK_HOME:-/root/labSpark/spark-4.2.0-bin-hadoop3}"
MASTER="${MASTER:-spark://192.168.100.3:7077}"
ROOT="${ROOT:-/root/fittrack}"
CURATED="${CURATED:-$ROOT/analytics/curated}"
CLEANING="${CLEANING:-$ROOT/analytics/data/cleaning.json}"
OUT="${OUT:-$ROOT/analytics/data/analytics.json}"
DRIVER_MEMORY="${DRIVER_MEMORY:-768m}"
EXECUTOR_MEMORY="${EXECUTOR_MEMORY:-1500m}"

mkdir -p "$(dirname "$OUT")"

"$SPARK_HOME/bin/spark-submit" \
  --master "$MASTER" \
  --driver-memory "$DRIVER_MEMORY" \
  --executor-memory "$EXECUTOR_MEMORY" \
  --conf spark.sql.shuffle.partitions=8 \
  "$ROOT/spark/analytics.py" \
  --curated "$CURATED" \
  --cleaning "$CLEANING" \
  --out "$OUT"
