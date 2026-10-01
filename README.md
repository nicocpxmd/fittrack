# FitTrack

Aplicación web de seguimiento físico basada en microservicios. Cada usuario registra medidas corporales, rutinas y metas, y consulta su progreso. Los datos de cada cuenta están aislados: ningún servicio entrega ni modifica registros de otro usuario.

## Arquitectura

Dos máquinas virtuales (Vagrant + VirtualBox, Ubuntu) conectadas por la red privada `192.168.100.0/24` (interfaz `eth1`):

| Máquina | IP | Qué corre |
|---|---|---|
| Ubuntu1 | `192.168.100.2` | nginx + página web (`frontend/index.html`) |
| Ubuntu2 | `192.168.100.3` | los cinco microservicios y sus bases de datos locales |

El navegador solo habla con nginx (puerto 80). nginx reenvía cada prefijo `/api/<servicio>/` al servicio correspondiente en Ubuntu2, por eso no hay problemas de CORS.

### Servicios

| Servicio | Puerto | Tecnología | Base de datos | Función |
|---|---|---|---|---|
| Users | 8002 | Python (FastAPI) | PostgreSQL | Registro, login (JWT), perfil, recuperación de contraseña |
| Measurements | 8001 | Python (FastAPI) | MongoDB | Medidas corporales |
| Progress | 8005 | Python (FastAPI) | MongoDB | Cálculo y registro del progreso entre dos fechas |
| Workouts | 8003 | Node.js (Express) | MySQL | Rutinas de entrenamiento |
| Goals | 8004 | Node.js (Express) | MySQL | Metas (subir o bajar una medida) |

### Rutas de nginx

| Desde el navegador | Servicio real |
|---|---|
| `/api/users/` | `192.168.100.3:8002/users/` |
| `/api/measurements/` | `192.168.100.3:8001/` |
| `/api/progress/` | `192.168.100.3:8005/progress/` |
| `/api/goals/` | `192.168.100.3:8004/goals/` |
| `/api/workouts/` | `192.168.100.3:8003/api/routines/` |

### Autenticación

Users emite un token JWT en el login. Los otros cuatro servicios no guardan usuarios: reciben `Authorization: Bearer <token>` y lo validan llamando a `GET /users/me` en Users. De ahí sacan el `user_id` y filtran todos los datos por él. Los parámetros `user_id` enviados en la URL se ignoran.

## Estructura del repositorio

```
frontend/index.html          Página (HTML + JavaScript, sin build)
services/
  users/ measurements/ progress/     Python (FastAPI)
  workouts/ goals/                   Node.js
  <servicio>/.env.example            Variables de entorno (sin valores reales)
deploy/
  nginx/fittrack.conf        Configuración de nginx (Ubuntu1)
  systemd/fittrack-*.service Unidades de arranque automático (Ubuntu2)
  netplan/98-fittrack-eth1.yaml  Ruta de red en Ubuntu2 (ver "Red")
```

## Requisitos

- Python 3 con `venv` (Users, Measurements, Progress)
- Node.js y npm (Workouts, Goals)
- PostgreSQL (Users), MySQL 8 o superior (Workouts y Goals; los `schema.sql` usan la collation `utf8mb4_0900_ai_ci`, que no existe en MariaDB ni en MySQL 5.7) y MongoDB (Measurements y Progress; en el proyecto se usó MongoDB Atlas)
- nginx (para la página)

## Puesta en marcha

### 1. Bases de datos

Goals y Workouts traen su `schema.sql` (estructura sin datos, exportada de la base real). Cambia `CLAVE` por una contraseña propia y usa esa misma en el `.env` del servicio.

- **MySQL (Goals y Workouts):**

  ```bash
  sudo mysql <<'EOF'
  CREATE DATABASE goals;
  CREATE DATABASE workouts;
  CREATE USER 'fittrack'@'localhost' IDENTIFIED BY 'CLAVE';
  GRANT ALL PRIVILEGES ON goals.*    TO 'fittrack'@'localhost';
  GRANT ALL PRIVILEGES ON workouts.* TO 'fittrack'@'localhost';
  EOF
  sudo mysql goals    < services/goals/schema.sql
  sudo mysql workouts < services/workouts/schema.sql
  ```

  En los `.env` de Goals y Workouts: `DB_HOST=localhost`, `DB_USER=fittrack`, `DB_PASSWORD=CLAVE` y `DB_NAME` con el nombre de cada base.

- **PostgreSQL (Users):** el repositorio no incluye el esquema de Users. Hay dos opciones:
  - Usar la base de PostgreSQL compartida del equipo (por ejemplo la de Supabase) poniendo su cadena de conexión en `DATABASE_URL`. Ya trae las tablas.
  - Crear una base propia y las tablas de Users a mano, con la misma estructura que la base compartida:

    ```bash
    sudo -u postgres psql <<'EOF'
    CREATE USER fittrack WITH PASSWORD 'CLAVE';
    CREATE DATABASE fittrack_users OWNER fittrack;
    EOF
    ```

    Luego `DATABASE_URL=postgresql+psycopg://fittrack:CLAVE@localhost:5432/fittrack_users`.

- **MongoDB (Measurements y Progress):** no hay esquema que cargar. Solo hacen falta la cadena de conexión (`MONGO_URL`) y el nombre de la base (`DB_NAME`); las colecciones se crean solas. Sirve un MongoDB local o un cluster de Atlas.

### 2. Variables de entorno

En cada carpeta de `services/`, copiar `.env.example` a `.env` y reemplazar los valores `CAMBIAR` por los reales:

| Servicio | Variables sensibles |
|---|---|
| Users | `DATABASE_URL`, `SECRET_KEY` |
| Measurements | `MONGO_URL` |
| Progress | `MONGO_URL` |
| Workouts | `DB_PASSWORD` |
| Goals | `DB_PASSWORD` |

`SECRET_KEY` firma los tokens de sesión: quien la conozca puede fabricar tokens válidos. Genera una propia y no uses ningún valor por defecto:

```bash
openssl rand -hex 32
```

Los archivos `.env` nunca se suben al repositorio (están en `.gitignore`). Las variables `USERS_SERVICE_URL`, `PROGRESS_SERVICE_URL` y `MEASUREMENTS_SERVICE_URL` deben apuntar a la IP y puerto de cada servicio (por defecto `http://192.168.100.3:<puerto>`).

### 3. Servicios de Python (Users, Measurements, Progress)

```bash
cd services/<servicio>
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/uvicorn main:app --host 0.0.0.0 --port <puerto>
```

Puertos: users `8002`, measurements `8001`, progress `8005`.

### 4. Servicios de Node (Workouts, Goals)

```bash
cd services/workouts && npm install && node index.js       # puerto 8003
cd services/goals    && npm install && node src/index.js   # puerto 8004
```

El puerto se toma de la variable `PORT` del `.env`.

### 5. Arranque automático con systemd (Ubuntu2)

Las unidades de `deploy/systemd/` arrancan los cinco servicios con la máquina y los reinician si se caen. Suponen el proyecto en `/home/vagrant/fittrack_taller/services` y el usuario `vagrant`; si tu ruta es distinta, edita `WorkingDirectory` y `ExecStart` antes de copiarlas.

```bash
sudo cp deploy/systemd/fittrack-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fittrack-users fittrack-measurements fittrack-progress fittrack-workouts fittrack-goals
systemctl is-active fittrack-users fittrack-measurements fittrack-progress fittrack-workouts fittrack-goals
```

Comandos útiles:

```bash
sudo systemctl restart fittrack-<nombre>        # tras cambiar código (no hay --reload)
journalctl -u fittrack-<nombre> -n 30 --no-pager  # ver por qué falló
```

### 6. Página y nginx (Ubuntu1)

```bash
sudo mkdir -p /var/www/fittrack
sudo cp frontend/index.html /var/www/fittrack/
sudo cp deploy/nginx/fittrack.conf /etc/nginx/sites-available/fittrack
sudo ln -s /etc/nginx/sites-available/fittrack /etc/nginx/sites-enabled/fittrack
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Abrir `http://192.168.100.2` en el navegador.

### 7. Red entre las VMs (Ubuntu2)

En el entorno de Vagrant, el DHCP de `eth0` instalaba una ruta `192.168.100.2 via 10.0.2.2`, y las respuestas hacia Ubuntu1 salían por la interfaz equivocada. `deploy/netplan/98-fittrack-eth1.yaml` agrega una ruta a `192.168.100.2/32` por `eth1` con menor métrica, y sobrevive a reinicios:

```bash
sudo cp deploy/netplan/98-fittrack-eth1.yaml /etc/netplan/
sudo chmod 600 /etc/netplan/98-fittrack-eth1.yaml
sudo netplan try
ip route get 192.168.100.2     # debe decir "dev eth1"
```

Solo aplica a este montaje con Vagrant. Con otra red no hace falta.

## Comportamiento de los servicios

- **Metas (Goals):** cada meta tiene una medida, un objetivo, una fecha límite y una dirección (`subir` o `bajar`). El porcentaje se calcula desde el valor inicial (la medida más antigua registrada de ese tipo) hasta el objetivo. Si no hay medidas de ese tipo, la meta no cambia. Al editar se pueden cambiar descripción, objetivo y fecha límite, pero no la medida ni la dirección.
- **Progreso (Progress):** `POST /progress/calculate` compara la primera y la última medida de un tipo dentro de un rango de fechas. Si ya existe un registro del mismo usuario, la misma medida y las mismas fechas, lo actualiza en lugar de duplicarlo. También existen `GET /progress/me` y `DELETE /progress/{id}`. El progreso no se edita a mano: se corrige la medida y se vuelve a calcular.
- **Medidas (Measurements):** el `PUT` mezcla los campos enviados con los existentes, así que un valor se puede cambiar pero no vaciar. Para quitarlo hay que eliminar la medida y registrarla de nuevo.
- **Rutinas (Workouts):** crear, listar, editar y eliminar solo las propias. Intentar borrar una ajena devuelve 403.

## Pruebas rápidas de humo

Desde Ubuntu1, con una cuenta ya registrada:

```bash
H=http://localhost
TOKEN=$(curl -s -X POST $H/api/users/login -H "Content-Type: application/json" \
  -d '{"email":"TU_CORREO","password":"TU_CLAVE"}' | jq -r .access_token)
for s in measurements goals workouts; do
  echo -n "$s: "; curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" $H/api/$s/
done
echo -n "progress: "; curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" $H/api/progress/me
```

Deben salir cuatro `200`. Sin token o con uno falso, los servicios responden 401 o 403.

## Limitaciones conocidas

- Las IPs (`192.168.100.2` y `192.168.100.3`) están escritas en la configuración de nginx y como valores por defecto en algunos servicios; para otro entorno hay que cambiarlas.
- Al editar una medida, los progresos ya guardados no se recalculan solos: hay que volver a pulsar "Calcular y guardar" con el mismo rango.
- La dirección (`subir` o `bajar`) de una meta no se puede cambiar después de crearla; se elimina y se vuelve a crear.
