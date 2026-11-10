#!/usr/bin/env bash
# Calcula los KPIs del dashboard a partir del Parquet curado.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

if [ -n "${SPARK_SUBMIT:-}" ]; then
  :
elif [ -n "${SPARK_HOME:-}" ] && [ -x "$SPARK_HOME/bin/spark-submit" ]; then
  SPARK_SUBMIT="$SPARK_HOME/bin/spark-submit"
else
  SPARK_SUBMIT="spark-submit"
fi

MASTER="${MASTER:-local[*]}"
CURATED="${CURATED:-$ROOT/analytics/curated}"
CLEANING="${CLEANING:-$ROOT/analytics/data/cleaning.json}"
OUT="${OUT:-$ROOT/analytics/data/analytics.json}"
DRIVER_MEMORY="${DRIVER_MEMORY:-768m}"
EXECUTOR_MEMORY="${EXECUTOR_MEMORY:-1500m}"

mkdir -p "$(dirname "$OUT")"

"$SPARK_SUBMIT" \
  --master "$MASTER" \
  --driver-memory "$DRIVER_MEMORY" \
  --executor-memory "$EXECUTOR_MEMORY" \
  --conf spark.sql.shuffle.partitions=8 \
  "$SCRIPT_DIR/analytics.py" \
  --curated "$CURATED" \
  --cleaning "$CLEANING" \
  --out "$OUT"
