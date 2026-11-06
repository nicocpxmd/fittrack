# Presentación — Proyecto final FitTrack

**Duración:** 15 minutos. **Formato:** 15 diapositivas. **Calificación:** individual.
**Regla:** cada integrante explica su parte; no leer las diapositivas.

## Reparto sugerido (5 personas)

| Minutos | Bloque | Quién |
|---|---|---|
| 0:00–1:30 | Título, problema y objetivos | A |
| 1:30–4:30 | Dataset y arquitectura | B |
| 4:30–8:00 | Parte 1: microservicios, Swarm, HAProxy y carga | C |
| 8:00–11:30 | Parte 2: pipeline Spark, limpieza y KPIs | D |
| 11:30–14:00 | Dashboard, API y demo | E |
| 14:00–15:00 | Conclusiones y trabajo futuro | A |

## Diapositiva 1 — Título

**FitTrack: microservicios en Docker Swarm y análisis distribuido con Apache Spark**

- Proyecto final — Redes e Infraestructura
- Integrantes
- Fecha

> Notas: presentarse, decir en una frase qué van a ver: una app real, un clúster y un pipeline de datos.

## Diapositiva 2 — Problema y objetivos

- Aplicación de seguimiento físico con 6 microservicios y 3 bases de datos.
- Reto 1: desplegarla en un clúster con escalabilidad y balanceo.
- Reto 2: procesar 8,4 M de filas y llevar los resultados al dashboard.
- Objetivos: empaquetar, desplegar, analizar, publicar, medir y documentar.

> Notas: aclarar que la app ya existía del primer módulo; el aporte es el empaquetado, el despliegue y el análisis.

## Diapositiva 3 — Dataset

- **FitTrack-Synth**: 100.000 usuarios, 8.462.080 filas, 741 MB.
- 78 semanas: 2025-01-06 a 2026-07-05.
- Sintético, reproducible (semilla 42) y autorizado por el profesor.
- Suciedad controlada: duplicados, nulos, fechas `dd/mm/aaaa`, libras, pesos absurdos.
- Validador: **24 chequeos OK, 0 con falla**.

> Notas: justificar por qué sintético: privacidad, reproducibilidad y patrones conocidos para validar. No ocultar que no es Kaggle; el profesor lo autorizó.

## Diapositiva 4 — Arquitectura

- Dos VMs: `servidorUbuntu` (manager) y `clienteUbuntu` (worker).
- HAProxy como único entrypoint; nginx solo sirve el frontend.
- 6 microservicios + Postgres, Mongo y MySQL.
- Servicio `analytics` lee el JSON de Spark.
- Spark master/worker en el servidor.

> Notas: mostrar el diagrama. Explicar que HAProxy enruta `/api/*` y balancea con `server-template`.

## Diapositiva 5 — Parte 1: microservicios y Swarm

- `users` (FastAPI/Postgres), `measurements` y `progress` (FastAPI/Mongo).
- `workouts` y `goals` (Node/MySQL).
- `docker-stack.yml` con placement, volúmenes y reinicio.
- HAProxy en `8080`, stats en `8404`.
- Frontend en `http://192.168.100.2:8080`.

> Notas: explicar la diferencia entre Compose (desarrollo) y stack (Swarm). Mencionar que las bases de datos se fijan al servidor por los volúmenes.

## Diapositiva 6 — Parte 1: balanceo y escalado

- HAProxy descubre tareas por DNS (`tasks.<servicio>`).
- `server-template` hasta 6 réplicas por servicio.
- Escalado con `docker service scale`.
- Prueba: 1 vs 3 réplicas de `users` y `measurements`.

> Notas: aclarar que las réplicas quedaron en el mismo nodo; el siguiente paso es repartirlas entre nodos.

## Diapositiva 7 — Resultados de carga

| Réplicas | RPS | p50 | p95 | Errores |
|---|---|---|---|---|
| 1 | 38,15 | 513,09 ms | 654,58 ms | 0 |
| 3 | **72,05** | **272,48 ms** | **411,70 ms** | 0 |

- **1,89×** más throughput.
- p50 −47 %, p95 −37 %.
- La primera prueba con 3 réplicas dio p95 3.485 ms por el swap de Spark; al detenerlo, mejoró.

> Notas: explicar que la medición se hizo con 500 peticiones y concurrencia 20 desde el host. La conclusión: el escalado funciona, pero compite con el batch.

## Diapositiva 8 — Parte 2: pipeline Spark

- CSV crudos → ETL → Parquet → KPIs → JSON → API → dashboard.
- ETL: esquema explícito, `try_to_date`, deduplicación, lb→kg, filtro 30–250 kg.
- KPIs: retención, adherencia, metas, peso, estacionalidad, rutinas.
- Servicio `analytics` (FastAPI) lee el JSON y lo publica.
- Spark no necesita estar encendido para el dashboard.

> Notas: mostrar el diagrama del pipeline. Destacar la separación batch/app.

## Diapositiva 9 — Limpieza

| Métrica | Valor |
|---|---|
| Duplicados de medidas | 14.204 |
| Duplicados de rutinas | 26.776 |
| Pesos inválidos | 2.925 |
| Fechas corregidas | 8.703 + 16.025 |
| Usuarios en libras | 14.659 |

- 2.881.725 medidas y 5.321.322 rutinas curadas.
- Los nulos de cintura/brazo/pecho se conservan; las agregaciones los ignoran.

> Notas: explicar por qué se conservan los nulos y por qué se filtra por 30–250 kg.

## Diapositiva 10 — KPIs y validación

| KPI | Valor |
|---|---|
| Activos a 12 semanas | 54.758 (54,8 %) |
| Sesiones/semana | 2,68 |
| Metas cumplidas | 16,96 % |
| Cambio medio de peso | −0,71 kg |
| Retención 4/12/26 semanas | 86,4 % / 51,6 % / 33,3 % |

| Patrón | Esperado | Obtenido |
|---|---|---|
| Abandono temprano | ~40 % | 39,53 % |
| Pico de enero | ≥1,4× | 1,88× |
| Corr. bajar peso | < −0,3 | −0,595 |
| Corr. ganar músculo | > 0,3 | +0,597 |

> Notas: esta es la diapositiva clave de la parte 2. El pipeline no solo corre: recupera los patrones que el generador sembró.

## Diapositiva 11 — Dashboard y demo

- Pestaña “Analítica” dentro de FitTrack.
- 5 tarjetas de KPIs, retención, metas, peso, estacionalidad y rutinas.
- Validación con etiquetas verdes.
- Demo: `http://192.168.100.2:8080` → iniciar sesión → Analítica.

> Notas: si la demo falla, usar la captura. Tener la sesión iniciada antes de presentar.

## Diapositiva 12 — API de analítica

- `GET /api/analytics/health`
- `GET /api/analytics/kpis`
- `GET /api/analytics/dashboard`
- `GET /api/analytics/retention`, `/goals`, `/weight`, `/seasonality`...

- FastAPI + JSON; cache por `mtime`; sin JDBC.
- HAProxy enruta `/api/analytics/*` a `analytics:8006`.

> Notas: mostrar un `curl` corto si hay tiempo.

## Diapositiva 13 — Pruebas y evidencias

- Dataset: 24/24 chequeos.
- API: registro/login/CRUD en las tres bases.
- Carga: 500 peticiones, 0 errores, 1 vs 3 réplicas.
- Dashboard: captura y endpoints 200.
- Reproducibilidad: README + scripts + `.env.example`.

> Notas: insistir en que cualquiera puede reproducirlo con el README.

## Diapositiva 14 — Decisiones y dificultades

- nginx fallaba con `host not found in upstream`: se dejó estático y HAProxy como entrypoint.
- Spark 4.2 con ANSI: `try_to_date` y ANSI off.
- Memoria: 3,8 GiB; Spark compite con el stack; se separaron las fases.
- Dataset sintético autorizado; no se buscó Kaggle.
- Las réplicas quedaron en un nodo; el escalado real entre nodos queda como trabajo futuro.

> Notas: esta diapositiva muestra criterio de ingeniería; no ocultar los problemas.

## Diapositiva 15 — Conclusiones y trabajo futuro

- App desplegada y balanceada; 1,89× al escalar.
- Pipeline Spark validado contra patrones sembrados.
- Dashboard con 100.000 usuarios y 8,4 M de filas.
- Trabajo futuro: Spark 2 nodos con NFS/HDFS, réplicas entre nodos, streaming, observabilidad y CI/CD.

> Notas: cerrar con la frase: “la solución funciona y es reproducible; el siguiente paso es distribuirla de verdad”.

## Preguntas probables

1. **¿Por qué Swarm y no Kubernetes?** Ya estaba inicializado, es nativo de Docker y suficiente para dos nodos; Kubernetes habría consumido más recursos.
2. **¿Por qué el dataset es sintético?** Privacidad, reproducibilidad y patrones conocidos; el profesor lo autorizó.
3. **¿Por qué no escriben a Postgres desde Spark?** Para no sumar un esquema/driver y permitir que el dashboard funcione sin Spark; el JSON es suficiente.
4. **¿Por qué el escalado no fue lineal?** Las réplicas comparten el mismo nodo y las mismas bases; el cuello es CPU/DB. Con dos nodos y réplicas repartidas se espera mejor.
5. **¿Qué pasa si Spark no corre?** El dashboard sigue funcionando: lee el JSON ya calculado. Solo se recalcula cuando se ejecuta el batch.
6. **¿Cómo se protegen los secretos?** `.env` fuera del repo, `.env.example` con valores falsos; `SECRET_KEY` de 64 caracteres.
