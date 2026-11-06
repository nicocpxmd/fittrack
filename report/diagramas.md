# Diagramas del informe

Estos diagramas están en Mermaid. GitHub los renderiza directamente; para el informe se exportan a
PNG en `report/figuras/`:

- `arquitectura.png` (Figura 1)
- `despliegue.png` (Figura 2)
- `pipeline.png` (Figura 3)

Se pueden renderizar en <https://mermaid.live> o con la extensión de Mermaid de VS Code.

## Figura 1 — Arquitectura de componentes

```mermaid
flowchart LR
  U[Usuario] --> LB[HAProxy<br/>:8080]
  LB -->|/| NG[nginx<br/>frontend]
  LB -->|/api/users| US[users<br/>:8002]
  LB -->|/api/measurements| ME[measurements<br/>:8001]
  LB -->|/api/progress| PR[progress<br/>:8005]
  LB -->|/api/goals| GO[goals<br/>:8004]
  LB -->|/api/workouts| WO[workouts<br/>:8003]
  LB -->|/api/analytics| AN[analytics<br/>:8006]

  US --> PG[(Postgres)]
  ME --> MO[(Mongo)]
  PR --> MO
  WO --> MY[(MySQL)]
  GO --> MY
  AN --> JS[(analytics.json)]

  DS[(dataset CSV)] --> SP[Spark<br/>ETL + KPIs]
  SP --> JS

  subgraph Cliente[clienteUbuntu]
    NG
    LB
  end

  subgraph Servidor[servidorUbuntu]
    US
    ME
    PR
    GO
    WO
    AN
    PG
    MO
    MY
    JS
    DS
    SP
  end
```

## Figura 2 — Diagrama de despliegue

```mermaid
flowchart TB
  subgraph Host[Windows host]
    NAV[Navegador]
  end

  subgraph Client[clienteUbuntu — 192.168.100.2 — Swarm worker]
    NG[nginx<br/>frontend estático]
    HA[HAProxy<br/>8080 / 8404]
  end

  subgraph Server[servidorUbuntu — 192.168.100.3 — Swarm manager]
    subgraph Services[Servicios]
      US[users]
      ME[measurements]
      PR[progress]
      GO[goals]
      WO[workouts]
      AN[analytics]
    end
    subgraph DBs[Bases de datos]
      PG[(Postgres)]
      MO[(Mongo)]
      MY[(MySQL)]
    end
    SPK[Spark master + worker<br/>:7077 / :8080]
    JSON[(analytics/data)]
  end

  NAV -->|HTTP| HA
  HA -->|/| NG
  HA -->|/api/*| Services
  US --> PG
  ME --> MO
  PR --> MO
  WO --> MY
  GO --> MY
  AN --> JSON
  SPK -->|ETL + KPIs| JSON
```

## Figura 3 — Pipeline de datos

```mermaid
flowchart LR
  CSV[CSV crudos<br/>8.462.080 filas · 741 MB] --> ETL[ETL Spark<br/>limpieza]
  ETL --> PQ[Parquet curado<br/>8.418.175 filas]
  PQ --> KPI[KPIs Spark<br/>retención, metas, peso]
  KPI --> JSON[analytics.json]
  JSON --> API[analytics API<br/>FastAPI :8006]
  API --> DASH[Dashboard<br/>pestaña Analítica]
```

## Figura 4 — Dashboard

La captura está en `report/figuras/dashboard.jpeg` y se referencia desde el informe. Corresponde a
la pestaña “Analítica” con los 100.000 usuarios y los KPIs calculados por Spark.
