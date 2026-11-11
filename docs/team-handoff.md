# Handoff del proyecto final — FitTrack + Spark

**Fecha:** 2026-11-11
**Entrega:** viernes 2026-11-20
**Versión de trabajo:** rama `proyecto-final` (README reproducible)
**Snapshot de entrega:** tag `v3.6-proyecto-final`

> **Para instalar y ejecutar, sigue el [`README.md`](../README.md).** Este documento describe el
> estado del proyecto; no repite la instalación.

## 1. Qué está hecho

| Parte | Estado | Evidencia |
|---|---|---|
| Microservicios en Docker Swarm | ✅ Desplegado | 7 backends de HAProxy en `UP` |
| Balanceo y escalado | ✅ Probado | 38,15 → 72,05 RPS en un nodo; 53–54 RPS multi-nodo, 0 errores |
| Failover de tarea | ✅ Probado | 99,70 % de éxito al matar 1 de 3 réplicas; recuperación en 8 s |
| Dataset sintético | ✅ 100k usuarios / 8,4 M filas | Validador 24/24 |
| ETL + KPIs con Spark | ✅ Ejecutado | `analytics/data/analytics.json` |
| API de analítica | ✅ Funcionando | `/api/analytics/*` |
| Pestaña “Analítica” | ✅ Funcionando | Captura en `report/figuras/dashboard.jpeg` |
| README reproducible | ✅ En el repo | `README.md` |
| Prueba de clon limpio | ✅ Superada | Clon del tag + Compose: 11 contenedores, 3 bases y dashboard |
| Informe IEEE | ✅ Compilado | `report/reporte.pdf`, 5 páginas |
| Diapositivas | 🟡 Borrador | `slides/slides.md` |
| Tag de entrega | ✅ Publicado | `v3.6-proyecto-final` |

## 2. Cómo verlo en 5 minutos en tu máquina

No necesitas las VMs ni la carpeta de otra persona. Solo Docker:

```bash
git clone -b v3.6-proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
cp .env.example .env
# editar .env con contraseñas alfanuméricas y una SECRET_KEY
mkdir -p analytics/data
cp analytics/sample/analytics.json analytics/data/analytics.json
docker compose up -d --build
```

> `v3.6-proyecto-final` es el snapshot congelado de la entrega. Para trabajar sobre el proyecto usa
> la rama `proyecto-final` (va un commit adelante, solo en documentación). `main` está atrasada hasta
> que se haga el merge.

En PowerShell:

```powershell
git clone -b v3.6-proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
Copy-Item .env.example .env
New-Item -ItemType Directory -Force analytics/data
Copy-Item analytics/sample/analytics.json analytics/data/analytics.json
docker compose up -d --build
```

Abrir `http://localhost:8080`, registrarse (cada uno crea su usuario) y entrar a **Analítica**.

Para el pipeline completo con Spark, seguir la sección 5 del `README.md`.

## 3. Qué falta

- **Diapositivas:** pasar `slides/slides.md` a PowerPoint/Google Slides y dejarlas en 15 minutos.
- **Sustentación:** guion y ensayo; si la presentación es pregrabada, también la grabación del video.
- **Guía de preguntas:** respuestas preparadas para el jurado (por qué Swarm y no Kubernetes, por qué
  el failover es de tarea y no de nodo, por qué el dataset es sintético, qué pasa si cae una base).
- **Entrega en UAO virtual:** subir el PDF del informe y las diapositivas.
- **Merge de `proyecto-final` a `main`:** `main` sigue atrasada; ver la sección 4.
- **Opcional:** worker de Spark en `clienteUbuntu` para medir 1 vs 2 workers. Requiere NFS o HDFS,
  porque con `file://` el Parquet quedaría repartido entre nodos.

## 4. Reglas de merge

- La entrega vive en `proyecto-final` y en el tag `v3.6-proyecto-final`.
- `main` no refleja la versión Docker; el merge es el pendiente #18 de `infraeip`.
- Antes de mergear: integrar `origin/main` dentro de `proyecto-final`, resolver conflictos
  (`services/goals`, `services/workouts/.env`, `README`, `docs/legacy/bare-metal/README.md`), probar
  el stack y revisar con el equipo.
- Los tags `v3.3`, `v3.4` y `v3.5` se conservan por si hay enlaces externos; **no se mueven**. `v3.2`
  se eliminó el 2026-11-11 y sus commits siguen en la rama.
- Mientras tanto, el link seguro para el Excel es:
  `https://github.com/nicocpxmd/fittrack/tree/v3.6-proyecto-final`.

## 5. Enlaces

| Qué | Dónde |
|---|---|
| Repo | `https://github.com/nicocpxmd/fittrack` |
| Tag de entrega | `https://github.com/nicocpxmd/fittrack/tree/v3.6-proyecto-final` |
| README (instalación) | `https://github.com/nicocpxmd/fittrack/blob/proyecto-final/README.md` |
| Informe (PDF) | `report/reporte.pdf` |
| Informe (LaTeX) | `report/reporte.tex` |
| Informe (Markdown) | `report/reporte.md` |
| Diagramas Mermaid | `report/diagramas.md` |
| Diapositivas | `slides/slides.md` |
| Consistencia dataset–app | `dataset/CONSISTENCIA.md` |
| Captura del dashboard | `report/figuras/dashboard.jpeg` |
| Guía sin Docker (legado) | `docs/legacy/bare-metal/README.md` |

Las rutas de archivo son relativas a la raíz del repositorio.
