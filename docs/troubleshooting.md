# Problemas comunes

[<- Volver al README](../README.md)


## El puerto 8080 o 8404 está ocupado

Primero identifica qué lo está usando:

```bash
docker compose ls
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

Si es otro stack de Compose, deténlo desde su carpeta:

```bash
cd <carpeta-del-stack-viejo>
docker compose down
```

Si el HAProxy del stack nuevo quedó creado sin puertos por el conflicto, recréalo:

```bash
cd <carpeta-del-stack-nuevo>
docker compose up -d --force-recreate haproxy
```

Si es otro proceso, ciérralo o cambia el mapeo en `docker-compose.yml` (`"8080:80"`,
`"8404:8404"`).

## El stack falla con `fe_sendauth: no password supplied`

`docker stack deploy` **no lee `.env` automáticamente**. Exporta las variables en la misma shell
donde despliegas:

```bash
cd /root/fittrack
set -a
. ./.env
set +a
docker stack deploy -c docker-stack.yml fittrack
```

Si el error persiste, revisa que `.env` tenga valores (sin mostrarlos):

```bash
awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/{print $1, "len=" length($2)}' .env
```

## `analytics` responde 503

Dos causas posibles:

1. **Falta `analytics/data/analytics.json`.** Copia la muestra del [README](../README.md) o corre
   [Spark](pipeline-spark.md).
2. **`analytics` no puede validar el token porque `users` no responde.** Revisa
   `docker compose ps users` y que `USERS_SERVICE_URL` apunte al servicio correcto
   (`http://users:8002` en Compose y en Swarm).

## La analítica responde 401 o 403

- **401**: no enviaste token o expiró (dura 60 minutos). Vuelve a iniciar sesión.
- **403**: el token es válido pero el usuario no tiene rol `admin`. Entra con `ADMIN_EMAIL` o revisa la
  columna `role` en la tabla `users`.

```bash
docker compose exec -T postgres psql -U fittrack -d fittrack_users \
  -c "SELECT email, role FROM users ORDER BY role;"
```

## No se creó el administrador

El servicio solo lo crea si `ADMIN_EMAIL` y `ADMIN_PASSWORD` están definidos **al arrancar**. Revisa el
log:

```bash
docker compose logs users | grep bootstrap
```

Si dice `no se crea administrador`, faltan las variables en el `.env` del proyecto o no se exportaron
antes de `docker stack deploy`. Agrégalas y reinicia el servicio; la operación es idempotente.

## `bad interpreter: /bin/bash^M`

Un script `.sh` se guardó con finales de línea Windows: el `#!/bin/bash` viaja con un `\r` y Linux lo
interpreta como un intérprete llamado `bash\r`. Pasa con `docker/mysql-init.sh`, que entonces no crea
los esquemas de `goals` y `workouts`.

```bash
file docker/mysql-init.sh        # debe decir "ASCII text", no "with CRLF line terminators"
sed -i 's/\r$//' docker/mysql-init.sh
```

El repositorio tiene `*.sh text eol=lf` en `.gitattributes`, así que un clon nuevo sale bien; el
problema aparece si editas el archivo en Windows.

## Las bases no arrancan o los esquemas no están

La primera inicialización de MySQL/Postgres tarda. Revisa:

```bash
docker compose logs mysql
docker compose logs users
```

Si el volumen se creó antes de tener los esquemas, el init no vuelve a correr. Para reiniciar desde
cero (borra datos):

```bash
docker compose down -v
docker compose up -d --build
```

## Spark no encuentra `spark-submit`

Instala Spark y define `SPARK_HOME`, o usa la imagen Docker de [Spark](pipeline-spark.md#ejecutar-spark). Si usas el host:

```bash
export SPARK_HOME="$HOME/spark-4.2.1-bin-hadoop3"
export PATH="$SPARK_HOME/bin:$PATH"
```

## Spark falla por memoria

El servidor de laboratorio tiene 3,8 GiB. Baja `EXECUTOR_MEMORY` o detén el stack mientras corre el
batch. En una máquina de 8 GB o más no debería ser problema.

## La imagen Docker de Spark no puede escribir

Usa `--user root` y `--entrypoint bash` como en [Spark](pipeline-spark.md#ejecutar-spark). El contenedor necesita escribir
`analytics/curated` y `analytics/data`.

## Windows: error con la ruta del volumen

En PowerShell usa `"${PWD}:/work"`; en bash, `"$PWD:/work"`. Docker Desktop debe tener habilitado el
acceso a la unidad del proyecto.

## Apple Silicon

El proyecto está probado en x86_64. `mongo:4.4` puede no tener imagen arm64; en un Mac ARM usa un
host x86_64, una VM Linux o ajusta la imagen de Mongo (no probado).

## `host not found in upstream` en nginx

El nginx del stack solo sirve el frontend estático; HAProxy es el único entrypoint de `/api/*`. No
vuelvas a agregar `proxy_pass` a servicios en `frontend/nginx.conf`.

## Spark y fechas `dd/mm/aaaa`

El ETL usa `try_to_date` y `spark.sql.ansi.enabled=false` para tolerar la suciedad controlada. No
cambies esas opciones sin revisar el ETL.

## Reset completo

```bash
# Compose: conserva volúmenes
docker compose down

# Compose: borra datos (irreversible)
docker compose down -v

# Swarm
docker stack rm fittrack
```

