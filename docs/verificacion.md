# Verificación: API, carga y failover

[<- Volver al README](../README.md)


## Contenedores

```bash
docker compose ps
# o, en Swarm:
docker stack services fittrack
```

## API y dashboard

```bash
# público
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/
curl -s http://localhost:8080/api/analytics/health

# la analítica exige administrador
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/analytics/kpis   # 401

TOKEN=$(curl -s -X POST http://localhost:8080/api/users/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@tudominio.com","password":"<tu ADMIN_PASSWORD>"}' \
  | python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/analytics/kpis   # 200

curl -s -o /dev/null -w "%{http_code}\n" -u admin:admin http://localhost:8404/
```

Esperado: `200` en el frontend, `"status":"ok"` en `/health`, `401` sin token, `200` con el token de
administrador y `200` en las stats.

En PowerShell, `python` puede no existir; usa `python3` o reemplaza la extracción por
`ConvertFrom-Json`.

> En Swarm, reemplaza `localhost` por `<worker-ip>` en estos comandos.

## Dataset

```bash
docker compose --profile tools run --rm dataset validar_dataset.py --dir /data
```

Esperado: **24 chequeos OK, 0 con falla**.

## Prueba de carga

```bash
python tests/load/load_test.py \
  --base http://localhost:8080 \
  --email demo@tudominio.com \
  --password 'ChangeMe123' \
  --requests 500 --concurrency 20
```

El script registra el usuario si no existe. Usa un correo de un dominio válido (el validador rechaza
dominios reservados como `.test`). No uses una cuenta real.

Resultados de referencia:

| Escenario | RPS | p50 | p95 | Errores |
|---|---|---|---|---|
| 1 réplica | 38,15 | 513,09 ms | 654,58 ms | 0 |
| 3 réplicas en un nodo | **72,05** | **272,48 ms** | **411,70 ms** | 0 |
| 3 réplicas en dos nodos | 53,31–54,22 | 278–304 ms | 839–871 ms | 0 |

La prueba multi-nodo repartió `users` 2+1 y `measurements` 1+2. El throughput baja frente a las 3
réplicas en un nodo por la red overlay y el worker de 2 cores; la distribución funciona, pero no es
una mejora de rendimiento en este laboratorio.

Prueba de estrés con `hey`, 30 segundos por nivel:

| Conexiones | RPS | p50 | p95 | Timeouts |
|---|---|---|---|---|
| 50 | 59,17 | 605 ms | 2.237 ms | 0 |
| 100 | 58,57 | 726 ms | 4.427 ms | 152 |
| 200 | 61,05 | 1.575 ms | 4.567 ms | 797 |

El RPS de `hey` cuenta solicitudes intentadas; el goodput baja a 53,6 RPS (100 conexiones) y 37,2
RPS (200) por los timeouts de 5 s. La meseta de ~60 RPS marca el punto de saturación del laboratorio.

## Prueba de failover

Con 3 réplicas de `users`, matar el contenedor de una tarea durante una carga sostenida:

```bash
# en el manager, mientras corre la carga
docker ps --filter name=fittrack_users --format '{{.ID}}  {{.Names}}'
docker kill $(docker ps -q --filter name=fittrack_users | head -n1)
```

Resultados de referencia (8.000 peticiones a `/api/users/me`, concurrencia 20):

| Escenario | Éxito | Errores | RPS | p95 |
|---|---|---|---|---|
| Control (sin fallo) | 100 % | 0 | 113,11 | 400,38 ms |
| Con failover | 99,70 % | 24 (0,30 %) | 97,61 | 400,66 ms |

Los 24 errores se concentran en los 8 segundos que tarda Swarm en recrear la tarea: 22 conexiones
cortadas (código 0) y 2 `502` de HAProxy. El p95 no cambia, así que las réplicas sobrevivientes
absorben el tráfico. Para que el cliente no vea los `502`, falta `option redispatch` y `retries` en
`haproxy/haproxy.cfg`.

Esta prueba solo cubre el fallo de una **tarea**. Si cae el nodo o la base de datos, el servicio no
se recupera solo.



## Prueba de aceptación

Una persona con Docker debe poder:

1. Clonar el repo en una carpeta limpia.
2. Crear `.env` (incluidas `ADMIN_EMAIL` y `ADMIN_PASSWORD`), copiar la muestra de analítica y ejecutar
   `docker compose up -d --build`.
3. Abrir `http://localhost:8080`, registrarse y comprobar que la pestaña **Analítica** *no* aparece.
4. Cerrar sesión, entrar con el administrador del `.env` y ver la pestaña **Analítica** con los KPIs.
5. Comprobar por API que sin rol no hay datos:
   `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/analytics/kpis` → `401`.
6. Opcional: generar un dataset pequeño y correr Spark en modo local.
7. Si algo falla, encontrar la causa en este README o en el troubleshooting.

Si un paso no se cumple, el README debe corregirse antes de la entrega.

