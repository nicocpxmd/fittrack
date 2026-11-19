# Estado final del proyecto — FitTrack + Spark

**Entrega:** viernes 2026-11-20
**Tag de entrega:** `v4.1-proyecto-final`
**Rama de trabajo:** `proyecto-final`
**Estado:** cerrado para entrega

> Para instalar y ejecutar, sigue el [`README.md`](../README.md). Este documento resume el estado
> final y los enlaces de la entrega; no repite la instalación.

## 1. Entregables

| Parte | Estado | Evidencia |
|---|---|---|
| Microservicios en Docker Swarm | ✅ Desplegado | 7 backends de HAProxy en `UP` |
| Balanceo y escalado | ✅ Probado | 38,15 → 72,05 RPS en un nodo; 53–54 RPS multi-nodo, 0 errores |
| Failover de tarea | ✅ Probado | 99,70 % de éxito al matar 1 de 3 réplicas; recuperación en 8 s |
| Acceso a la analítica | ✅ Restringido | 401 sin token, 403 con usuario, 200 con administrador |
| Dataset sintético | ✅ 100k usuarios / 8,4 M filas | Validador 24/24 |
| ETL + KPIs con Spark | ✅ Ejecutado | `analytics/data/analytics.json` |
| API de analítica | ✅ Funcionando | `/api/analytics/*` |
| Pestaña “Analítica” | ✅ Funcionando | Captura en `report/figuras/dashboard.jpeg` |
| README reproducible | ✅ En el repo | `README.md` |
| Prueba de clon limpio | ✅ Superada | Clon del tag + Compose: 11 contenedores, 3 bases y dashboard |
| Informe IEEE | ✅ 7 páginas | `report/reporte.pdf` |
| Diapositivas | ✅ 18 páginas | `slides/fittrack.pdf` |
| Video de demostración | ✅ 2:00, sin audio | Archivo aparte, no versionado |
| Guiones individuales | ✅ 5 PDF | Repositorio privado del equipo, fuera de la entrega |
| Tag de entrega | ✅ Publicado | `v4.1-proyecto-final` |

## 2. Cómo verlo en 5 minutos en tu máquina

No necesitas las VMs ni la carpeta de otra persona. Solo Docker:

```bash
git clone -b v4.1-proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
cp .env.example .env
# editar .env con contraseñas alfanuméricas y una SECRET_KEY
mkdir -p analytics/data
cp analytics/sample/analytics.json analytics/data/analytics.json
docker compose up -d --build
```

En PowerShell:

```powershell
git clone -b v4.1-proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
Copy-Item .env.example .env
New-Item -ItemType Directory -Force analytics/data
Copy-Item analytics/sample/analytics.json analytics/data/analytics.json
docker compose up -d --build
```

Abrir `http://localhost:8080`, registrarse (cada uno crea su usuario) y comprobar que la pestaña
**Analítica** no aparece: es solo para administradores. Para verla, cierra sesión y entra con
`ADMIN_EMAIL` / `ADMIN_PASSWORD` del `.env`.

Para el pipeline completo con Spark, seguir [`pipeline-spark.md`](pipeline-spark.md).

## 3. Estado de las ramas

- La entrega vive en la rama `proyecto-final` y en el tag `v4.1-proyecto-final`.
- La rama `main` quedó en una versión anterior; no se usa para desplegar.
- Los tags `v3.3`, `v3.4`, `v3.5`, `v3.7`, `v3.8`, `v3.9` y `v4.0` se conservan por si hay enlaces
  externos. `v3.2` y `v3.6` se eliminaron el 2026-11-11 y sus commits siguen en la rama.

## 4. Enlaces

| Qué | Dónde |
|---|---|
| Repo | `https://github.com/nicocpxmd/fittrack` |
| Tag de entrega | `https://github.com/nicocpxmd/fittrack/tree/v4.1-proyecto-final` |
| README (instalación) | `https://github.com/nicocpxmd/fittrack/blob/v4.1-proyecto-final/README.md` |
| Informe (PDF, 7 páginas) | `report/reporte.pdf` |
| Informe (LaTeX) | `report/reporte.tex` |
| Informe (Markdown de trabajo) | `report/reporte.md` |
| Diagramas Mermaid | `report/diagramas.md` |
| Diapositivas (PDF, 18 páginas) | `slides/fittrack.pdf` |
| Fuente de las diapositivas | `slides/slides.md` |
| Consistencia dataset–app | `dataset/CONSISTENCIA.md` |
| Captura del dashboard | `report/figuras/dashboard.jpeg` |
| Guía sin Docker (legado) | `docs/legacy/bare-metal/README.md` |

Las rutas de archivo son relativas a la raíz del repositorio.
