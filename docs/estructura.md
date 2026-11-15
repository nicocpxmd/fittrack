# Estructura del repositorio

[<- Volver al README](../README.md)


```text
analytics/                 API FastAPI + muestra de analítica
  main.py
  sample/analytics.json
dataset/                   generador, validador, diccionario y consistencia
frontend/                  HTML/JS del dashboard (incluye pestaña Analítica)
haproxy/                   configuración de entrada (stack y compose)
services/                  users, measurements, progress, workouts, goals
spark/                     ETL, KPIs y scripts de ejecución
tests/load/                prueba de carga sin dependencias
report/                    informe IEEE, figuras y PDF
slides/                    diapositivas de la sustentación
docs/
  team-handoff.md          estado y tareas del equipo
  api-contracts/           contratos de API
  legacy/bare-metal/       guía y deploy del montaje sin Docker (histórico)
docker-compose.yml         ejecución local en una máquina
docker-stack.yml           despliegue en Swarm
.env.example               variables de ejemplo
```

Directorios generados e ignorados por Git:

- `dataset/data/` (CSV del dataset)
- `analytics/curated/` (Parquet)
- `analytics/data/` (JSON de KPIs)
- `tests/load/*.json` (resultados de carga)

