#!/usr/bin/env bash
# ETL + KPIs en secuencia.
set -euo pipefail

ROOT="${ROOT:-/root/fittrack}"
"$ROOT/spark/run_etl.sh"
"$ROOT/spark/run_analytics.sh"
