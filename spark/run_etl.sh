#!/usr/bin/env bash
# Ejecuta el ETL sobre el dataset crudo de FitTrack-Synth.
set -euo pipefail

SPARK_HOME="${SPARK_HOME:-/root/labSpark/spark-4.2.0-bin-hadoop3}"
MASTER="${MASTER:-spark://192.168.100.3:7077}"
ROOT="${ROOT:-/root/fittrack}"
RAW="${RAW:-$ROOT/dataset/data}"
CURATED="${CURATED:-$ROOT/analytics/curated}"
REPORT="${REPORT:-$ROOT/analytics/data/cleaning.json}"
DRIVER_MEMORY="${DRIVER_MEMORY:-768m}"
EXECUTOR_MEMORY="${EXECUTOR_MEMORY:-1500m}"

mkdir -p "$CURATED" "$(dirname "$REPORT")"

"$SPARK_HOME/bin/spark-submit" \
  --master "$MASTER" \
  --driver-memory "$DRIVER_MEMORY" \
  --executor-memory "$EXECUTOR_MEMORY" \
  --conf spark.sql.shuffle.partitions=8 \
  "$ROOT/spark/etl.py" \
  --raw "$RAW" \
  --curated "$CURATED" \
  --report "$REPORT"
