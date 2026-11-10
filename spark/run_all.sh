#!/usr/bin/env bash
# ETL + KPIs en secuencia.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/run_etl.sh"
bash "$SCRIPT_DIR/run_analytics.sh"
