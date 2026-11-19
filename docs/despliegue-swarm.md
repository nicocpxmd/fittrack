# Modo clúster con Docker Swarm

[<- Volver al README](../README.md)


Esta es la ruta que cumple el requisito de clúster del enunciado. Requiere dos hosts Linux con
Docker.

## Inicializar el Swarm

En el nodo que será manager:

```bash
docker swarm init --advertise-addr <server-ip>
```

Copia el comando `docker swarm join --token ...` que imprime y ejecútalo en el worker:

```bash
docker swarm join --token <token> <server-ip>:2377
```

Verifica:

```bash
docker node ls
```

## Etiquetar los nodos

El stack usa labels, no hostnames:

```bash
docker node update --label-add role=server <hostname-del-manager>
docker node update --label-add role=worker <hostname-del-worker>
```

Si un nodo tiene las dos funciones, puedes ponerle ambos labels; pero el stack espera al menos un
nodo `role=server` y uno `role=worker`.

## Repositorio y ruta

Clona el repo en el nodo **server** (en el laboratorio, el manager). El stack usa
`${FITTRACK_DIR:-/root/fittrack}` para los bind mounts de MySQL y `analytics`:

```bash
cd /ruta/al/fittrack
export FITTRACK_DIR="$PWD"
```

Si el repo está en `/root/fittrack`, no hace falta exportar nada: es el valor por defecto.

## Imágenes

El stack usa las imágenes publicadas `nicocpxm/fittrack-*`. Si no tienes acceso o cambiaste código,
construye y publica en **tu** namespace y actualiza los `image:` del stack:

```bash
docker build -t <tu-usuario>/fittrack-nginx:v5 ./frontend
docker build -t <tu-usuario>/fittrack-haproxy:v2 ./haproxy
docker build -t <tu-usuario>/fittrack-analytics:v2 ./analytics
docker push <tu-usuario>/fittrack-nginx:v5
docker push <tu-usuario>/fittrack-haproxy:v2
docker push <tu-usuario>/fittrack-analytics:v2
```

Los servicios `users`, `measurements`, `progress`, `workouts` y `goals` también tienen imágenes
publicadas; si las reconstruyes, actualiza sus tags.

## Desplegar

```bash
set -a
. ./.env
set +a
export FITTRACK_DIR="${FITTRACK_DIR:-$PWD}"
docker stack deploy -c docker-stack.yml fittrack
docker stack services fittrack
```

Espera a que los servicios estén en su número de réplicas: `1/1` para las bases, `analytics`, `nginx`
y `haproxy`, y `3/3` para `users` y `measurements`. El entrypoint es `http://<worker-ip>:8080`; las
stats de HAProxy, `http://<worker-ip>:8404` (admin / admin).

> `ADMIN_EMAIL` y `ADMIN_PASSWORD` tienen que estar en el `.env` **antes** de desplegar: el servicio de
> usuarios los lee al arrancar para crear el administrador. Si el stack ya existía con una base
> anterior, aplica primero la migración de [configuración](configuracion.md#roles-y-acceso).

## Escalar

El stack ya declara **3 réplicas** para `users` y `measurements`, que es la topología de las pruebas
de carga y failover. Un `docker stack deploy` las mantiene; no hay que escalar a mano después.

Para cambiarlas en caliente:

```bash
docker service scale fittrack_users=3 fittrack_measurements=3
docker stack services fittrack
```

Ojo: `docker service scale` no modifica `docker-stack.yml`. El siguiente `docker stack deploy`
vuelve a lo que diga el archivo, así que si quieres conservar otro número, edítalo ahí.

Las réplicas de servicios sin estado se reparten entre los nodos según los labels y la
disponibilidad. `max_replicas_per_node: 2` y `spread: node.labels.role` hacen que con 3 réplicas
caigan 2+1. En el laboratorio, `users` quedó 2+1 y `measurements` 1+2.

**Si tu Swarm tiene un solo nodo**, `max_replicas_per_node: 2` deja la tercera tarea en estado
`Pending`. Baja a 2 réplicas en `docker-stack.yml` o sube ese límite. Los servicios con estado
permanecen en `role=server`.

## Notas del laboratorio

El laboratorio del curso usó dos VMs (una manager y una worker) y un servidor Spark local. Esa
configuración específica está documentada en el repo de infraestructura del curso. Este README usa
placeholders para que funcione en cualquier entorno; si usas el laboratorio, reemplaza
`<server-ip>` y `<worker-ip>` por las IPs de tus VMs y etiqueta los nodos como se indica.

