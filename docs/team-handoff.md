# Handoff del proyecto final — FitTrack + Spark

**Fecha:** 2026-11-11
**Entrega:** viernes 2026-11-20
**Versión de trabajo:** rama `proyecto-final` (README reproducible)
**Snapshot de entrega:** tag `v3.5-proyecto-final`

> **Para instalar y ejecutar, sigue el [`README.md`](../README.md).** Este documento es el estado del
> proyecto y el reparto de tareas del equipo; no repite la instalación.

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
| Informe y diapositivas | 🟡 Borradores | `report/` y `slides/` |
| Tag de entrega | ✅ Publicado | `v3.5-proyecto-final` |

**Lo que no está hecho:** el PDF IEEE final, las diapositivas en PowerPoint/Google Slides, el merge a
`main` y (opcional) el worker Spark en el cliente.

## 2. Cómo verlo en 5 minutos en tu máquina

No necesitas las VMs ni la carpeta de otra persona. Solo Docker:

```bash
git clone -b proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
cp .env.example .env
# editar .env con contraseñas alfanuméricas y una SECRET_KEY
mkdir -p analytics/data
cp analytics/sample/analytics.json analytics/data/analytics.json
docker compose up -d --build
```

> `main` está atrasada; clona `proyecto-final` hasta que se haga el merge.

En PowerShell:

```powershell
git clone -b proyecto-final https://github.com/nicocpxmd/fittrack.git
cd fittrack
Copy-Item .env.example .env
New-Item -ItemType Directory -Force analytics/data
Copy-Item analytics/sample/analytics.json analytics/data/analytics.json
docker compose up -d --build
```

Abrir `http://localhost:8080`, registrarse (cada uno crea su usuario) y entrar a **Analítica**.

Para el pipeline completo con Spark, seguir la sección 5 del `README.md`.

## 3. Demo del laboratorio (opcional)

Si tienes acceso a las VMs del laboratorio, pide la IP del equipo y usa la cuenta que crees tú mismo.
No se publican credenciales ni rutas personales. El laboratorio ya tiene el stack desplegado; para
replicarlo desde cero, sigue la sección 6 del `README.md`.

## 4. Qué falta y reparto propuesto

| # | Tarea | Quién | Fecha |
|---|---|---|---|
| 1 | Informe IEEE: compilar `report/reporte.tex` en Overleaf, revisar 10 páginas, exportar PDF | A | 2026-11-13 |
| 2 | Diapositivas: pasar `slides/slides.md` a PowerPoint/Google Slides | B | 2026-11-13 |
| 3 | Merge de `proyecto-final` a `main` con revisión del equipo | D | 2026-11-16 |
| 4 | Ensayo de los 15 minutos y reparto de bloques | E | 2026-11-17 |
| 5 | Subir PDF y diapositivas a UAO virtual y al repo | A/E | 2026-11-18 |

Ajustar los nombres según el equipo. La idea es que cada persona tenga una tarea concreta y una fecha.
La prueba de failover ya está hecha (2026-11-11) y documentada en la sección 5.5 del informe.

## 5. Qué necesito de cada uno

1. **Probar el quick start del `README.md`** en su propia máquina; si algo falla, reportarlo.
2. **Revisar la rama `proyecto-final`** y el `README.md`; no hace falta leer los 54 archivos del diff.
3. **Elegir una tarea** de la tabla y ponerle fecha.
4. **No mergear a `main` sin revisión**: la rama `main` está atrasada y el merge tiene conflictos
   conocidos (goals, `.env` de workouts, README, guía legacy).
5. **No tocar** `dataset/data` ni los volúmenes de las bases sin avisar.
6. **No publicar credenciales** en el repo ni en el chat del grupo.

## 6. Reglas de merge

- La entrega vive en `proyecto-final` y en el tag `v3.5-proyecto-final`.
- `main` no refleja la versión Docker; el merge es el pendiente #18 de `infraeip`.
- Antes de mergear: integrar `origin/main` dentro de `proyecto-final`, resolver conflictos
  (`services/goals`, `services/workouts/.env`, `README`, `docs/legacy/bare-metal/README.md`), probar
  el stack y revisar con el equipo.
- Los tags `v3.2`, `v3.3` y `v3.4` se conservan por si hay enlaces externos; **no se mueven**.
- Mientras tanto, el link seguro para el Excel es:
  `https://github.com/nicocpxmd/fittrack/tree/v3.5-proyecto-final`.

## 7. Enlaces

| Qué | Dónde |
|---|---|
| Repo | `https://github.com/nicocpxmd/fittrack` |
| Tag de entrega | `https://github.com/nicocpxmd/fittrack/tree/v3.5-proyecto-final` |
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

## 8. Decisiones que hay que poder defender

- **Dataset sintético autorizado** por el profesor; no se buscó Kaggle. Generador reproducible en
  `dataset/`, validado 24/24.
- **nginx solo sirve el frontend**; HAProxy es el único entrypoint de `/api/*` (D17).
- **Spark escribe Parquet/JSON, no JDBC**: el dashboard funciona sin Spark encendido (D18).
- **Los 4 objetivos del dataset** (`bajar_peso`, `ganar_musculo`, `mantener`, `resistencia`) son el
  perfil del usuario, no la dirección de una meta. `subir/bajar` es `goals.direccion` (D16 y
  `dataset/CONSISTENCIA.md`).
- **Las réplicas se distribuyen entre nodos**: con `max_replicas_per_node: 2` y labels,
  `users` quedó 2+1 y `measurements` 1+2; el throughput multi-nodo es menor por overlay y por el
  worker de 2 cores.
- **Compose es la ruta de reproducción local; Swarm es el clúster evaluado**. El enunciado no
  impone una herramienta, pero sí exige un clúster.

## 9. Calendario 10–20 de noviembre

| Fecha | Hito |
|---|---|
| Mar 10 | Verificar stack, exportar figuras, repartir tareas |
| Mié 11 | Informe IEEE con figuras y consistencia |
| Jue 12 | Diapositivas en PowerPoint/Google Slides |
| Vie 13 | Ensayo 1 con la evidencia de failover |
| Sáb 14 – Dom 15 | Ajustes |
| Lun 16 | Merge a `main` con revisión |
| Mar 17 | Ensayo 2 y capturas de respaldo |
| Mié 18 | Congelar y subir a UAO virtual |
| Jue 19 | Buffer y ensayo final |
| Vie 20 | Entrega |

## 10. Mensaje para el grupo

> Hola equipo. La parte operativa del proyecto está terminada en la rama `proyecto-final`; el
> snapshot de entrega es el tag `v3.5-proyecto-final`. Para verla en su máquina no necesitan mis
> rutas ni mis VMs: clonan con `-b proyecto-final`, siguen el `README.md` y ejecutan
> `docker compose up -d --build`. Cada uno crea su propio usuario; no hay credenciales compartidas.
>
> Lo que falta es documentación: el PDF IEEE, las diapositivas y el ensayo. Revisen la rama, prueben
> el quick start y elijan una tarea de `docs/team-handoff.md`. No mergeemos a `main` sin revisar.
>
> Link de la versión de trabajo: https://github.com/nicocpxmd/fittrack/tree/proyecto-final
