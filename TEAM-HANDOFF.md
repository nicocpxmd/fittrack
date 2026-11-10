# Handoff del proyecto final — FitTrack + Spark

**Fecha:** 2026-11-10
**Entrega:** viernes 2026-11-20
**Versión congelada:** tag `v3.1-proyecto-final`
**Rama de trabajo:** `proyecto-final`

Este documento es el punto único de entrada para el equipo. Resume qué está hecho, cómo verlo en
10 minutos, qué falta y cómo repartirlo.

## 1. Qué está hecho

| Parte | Estado | Evidencia |
|---|---|---|
| Microservicios en Docker Swarm | ✅ Desplegado | 7 backends de HAProxy en `UP` |
| Balanceo y escalado | ✅ Probado | 38,15 → 72,05 RPS con 3 réplicas, 0 errores |
| Dataset sintético | ✅ 100k usuarios / 8,4 M filas | Validador 24/24 |
| ETL + KPIs con Spark | ✅ Ejecutado | `analytics/data/analytics.json` |
| API de analítica | ✅ Funcionando | `/api/analytics/*` |
| Pestaña “Analítica” | ✅ Funcionando | Captura en `report/figuras/dashboard.jpeg` |
| README paso a paso | ✅ En el repo | `README.md` |
| Informe y diapositivas | 🟡 Borradores | `report/` y `slides/` |
| Tag de entrega | ✅ Publicado | `v3.0` y `v3.1` |

**Lo que no está hecho:** el PDF IEEE final, las diapositivas en PowerPoint/Google Slides, la prueba
de failover, el merge a `main` y (opcional) el worker Spark en el cliente.

## 2. Cómo verlo en 10 minutos

```powershell
# 1. Encender las VMs
cd C:\Users\nicoc\Documents\infraeip
vagrant up
vagrant status

# 2. Abrir el dashboard
# http://192.168.100.2:8080
# usuario de prueba: audit20261105@gmail.com / Password123

# 3. Ver la API de analítica
# http://192.168.100.2:8080/api/analytics/health
# http://192.168.100.2:8080/api/analytics/kpis

# 4. Stats de HAProxy
# http://192.168.100.2:8404  (admin / admin)
```

En el dashboard: iniciar sesión → pestaña **Analítica**. Se ven 5 KPIs, retención, metas, peso,
estacionalidad, rutinas y la validación contra los patrones sembrados.

## 3. Qué falta y reparto propuesto

| # | Tarea | Quién | Fecha |
|---|---|---|---|
| 1 | Informe IEEE: compilar `report/reporte.tex` en Overleaf, revisar 10 páginas, exportar PDF | A | 2026-11-13 |
| 2 | Diapositivas: pasar `slides/slides.md` a PowerPoint/Google Slides | B | 2026-11-13 |
| 3 | Failover de HAProxy y captura de evidencia | C | 2026-11-12 |
| 4 | Merge de `proyecto-final` a `main` con revisión del equipo | D | 2026-11-16 |
| 5 | Ensayo de los 15 minutos y reparto de bloques | E | 2026-11-17 |
| 6 | Subir PDF y diapositivas a UAO virtual y al repo | A/E | 2026-11-18 |

Ajustar los nombres según el equipo. La idea es que cada persona tenga una tarea concreta y una fecha.

## 4. Qué necesito de cada uno

1. **Revisar el tag `v3.1`** y el `README.md`; no hace falta leer los 54 archivos del diff.
2. **Probar la demo** con la cuenta de prueba y confirmar que el dashboard abre.
3. **Elegir una tarea** de la tabla y ponerle fecha.
4. **No mergear a `main` sin revisión**: la rama `main` está atrasada y el merge tiene conflictos
   conocidos (goals, `.env` de workouts, README, guía).
5. **No tocar** `dataset/data` ni los volúmenes de las bases sin avisar.

## 5. Reglas de merge

- La entrega vive en `proyecto-final` y en el tag `v3.1-proyecto-final`.
- `main` **no** refleja la versión Docker; el merge es el pendiente #18 de `infraeip`.
- Antes de mergear: integrar `origin/main` dentro de `proyecto-final`, resolver conflictos
  (`services/goals`, `services/workouts/.env`, `README`, `GUIA PARA FITTRACK.md`), probar el stack
  y revisar con el equipo.
- Después: tag nuevo `v3.2.0`; **no mover `v3.1`**.
- Mientras tanto, el link seguro para el Excel es:
  `https://github.com/nicocpxmd/fittrack/tree/v3.1-proyecto-final`.

## 6. Enlaces

| Qué | Dónde |
|---|---|
| Repo | `https://github.com/nicocpxmd/fittrack` |
| Tag de entrega | `https://github.com/nicocpxmd/fittrack/tree/v3.1-proyecto-final` |
| README | `https://github.com/nicocpxmd/fittrack/blob/v3.1-proyecto-final/README.md` |
| Informe (LaTeX) | `report/reporte.tex` |
| Informe (Markdown) | `report/reporte.md` |
| Diagramas Mermaid | `report/diagramas.md` |
| Diapositivas | `slides/slides.md` |
| Consistencia dataset–app | `dataset/CONSISTENCIA.md` |
| Captura del dashboard | `report/figuras/dashboard.jpeg` |
| Ficha en infraeip | `docs/practicas/proyecto-final.md` |

## 7. Mensaje para el grupo

> Hola equipo. La parte operativa del proyecto final ya está terminada y desplegada: Swarm con los
> microservicios, HAProxy balanceando, Spark procesando 8,4 M de filas y la pestaña “Analítica” en el
> dashboard. Está todo congelado en el tag `v3.1-proyecto-final`.
>
> Lo que falta es documentación: el PDF IEEE, las diapositivas y el ensayo. Dejé el contenido del
> informe y las diapositivas en `report/` y `slides/`, y un documento de handoff con el estado, los
> enlaces y las tareas en `TEAM-HANDOFF.md`.
>
> Por favor revisen el tag y el README, prueben la demo y elijan una tarea de la tabla. No mergeemos a
> `main` sin revisar: esa rama está atrasada y hay conflictos conocidos.
>
> Link de la versión: https://github.com/nicocpxmd/fittrack/tree/v3.1-proyecto-final

## 8. Decisiones que hay que poder defender

- **Dataset sintético autorizado** por el profesor; no se buscó Kaggle. Generador reproducible en
  `dataset/`, validado 24/24.
- **nginx solo sirve el frontend**; HAProxy es el único entrypoint de `/api/*` (D17).
- **Spark escribe Parquet/JSON, no JDBC**: el dashboard funciona sin Spark encendido (D18).
- **Los 4 objetivos del dataset** (`bajar_peso`, `ganar_musculo`, `mantener`, `resistencia`) son el
  perfil del usuario, no la dirección de una meta. `subir/bajar` es `goals.direccion` (D16 y
  `dataset/CONSISTENCIA.md`).
- **Las réplicas quedaron en un nodo**: el escalado es dentro del servidor; distribuir entre nodos
  es trabajo futuro.

## 9. Calendario 10–20 de noviembre

| Fecha | Hito |
|---|---|
| Mar 10 | Verificar stack, exportar figuras, repartir tareas |
| Mié 11 | Informe IEEE con figuras y consistencia |
| Jue 12 | Diapositivas en PowerPoint/Google Slides |
| Vie 13 | Failover de HAProxy y ensayo 1 |
| Sáb 14 – Dom 15 | Ajustes |
| Lun 16 | Merge a `main` con revisión |
| Mar 17 | Ensayo 2 y capturas de respaldo |
| Mié 18 | Congelar y subir a UAO virtual |
| Jue 19 | Buffer y ensayo final |
| Vie 20 | Entrega |
