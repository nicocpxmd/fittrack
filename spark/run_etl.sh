#!/usr/bin/env bash
# Ejecuta el ETL sobre el dataset crudo de FitTrack-Synth.
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
RAW="${RAW:-$ROOT/dataset/data}"
CURATED="${CURATED:-$ROOT/analytics/curated}"
REPORT="${REPORT:-$ROOT/analytics/data/cleaning.json}"
DRIVER_MEMORY="${DRIVER_MEMORY:-768m}"
EXECUTOR_MEMORY="${EXECUTOR_MEMORY:-1500m}"

mkdir -p "$CURATED" "$(dirname "$REPORT")"

"$SPARK_SUBMIT" \
  --master "$MASTER" \
  --driver-memory "$DRIVER_MEMORY" \
  --executor-memory "$EXECUTOR_MEMORY" \
  --conf spark.sql.shuffle.partitions=8 \
  "$SCRIPT_DIR/etl.py" \
  --raw "$RAW" \
  --curated "$CURATED" \
  --report "$REPORT"
