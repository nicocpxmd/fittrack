# Microservicio Frontend - Rutinas (rutinas.html)
Ubicación en el servidor: `/var/www/html/rutinas.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>FitTrack - Gestión de Rutinas</title>
    <link href="[https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css](https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css)" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #0d9488;">
    <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="index.html">💪 FitTrack - Rutinas</a>
        <ul class="navbar-nav me-auto">
            <li class="nav-item"><a class="nav-link" href="index.html">🏠 Inicio (Portal)</a></li>
            <li class="nav-item"><a class="nav-link active" href="rutinas.html">🏋️‍♂️ Gestionar Rutinas</a></li>
        </ul>
    </div>
</nav>

<div class="container mt-4 mb-5">
    <h2 class="text-center mb-4">Gestión de Rutinas de Entrenamiento</h2>

    <!-- Formulario Crear / Editar -->
    <div class="card p-4 shadow-sm mb-4">
        <h4 id="formTitle">Crear Nueva Rutina</h4>
        <input type="hidden" id="editId">
        <div id="rutinaForm">
            <div class="mb-3">
                <label class="form-label">Nombre de la Rutina:</label>
                <input type="text" id="nombre_rutina" class="form-control" placeholder="Ej. Día de Pierna Pesado" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Tipo de Enfoque:</label>
                <select id="tipo_enfoque" class="form-select" required>
                    <option value="">Seleccione el enfoque...</option>
                    <option value="Musculo Individual">Músculo Individual</option>
                    <option value="Push-Pull-Legs">Push-Pull-Legs (PPL)</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Grupo Muscular / Categoría:</label>
                <select id="grupo_muscular" class="form-select" required>
                    <option value="">Primero seleccione el enfoque...</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Ejercicios:</label>
                <textarea id="ejercicios" class="form-control" rows="3" placeholder="Ej. Sentadillas, Extensiones, Prensa" required></textarea>
            </div>
            <div class="mb-3">
                <label class="form-label">Fecha:</label>
                <input type="date" id="fecha_creacion" class="form-control" required>
            </div>
            <button type="button" id="btnGuardar" class="btn btn-success w-100">Guardar Rutina</button>
            <button type="button" id="btnCancelar" class="btn btn-secondary w-100 mt-2 d-none" onclick="resetFormulario()">Cancelar Edición</button>
        </div>
        <div id="msg" class="mt-3"></div>
    </div>

    <!-- Tabla de Listado -->
    <div class="card p-4 shadow-sm">
        <h4>Rutinas Registradas</h4>
        <table class="table table-striped table-bordered text-center mt-3">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Enfoque</th>
                    <th>Grupo / Categoría</th>
                    <th>Ejercicios</th>
                    <th>Fecha</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="tablaRutinas"></tbody>
        </table>
    </div>
</div>

<script>
const API_URL = '[http://192.168.100.3:3000/api/routines](http://192.168.100.3:3000/api/routines)';

document.getElementById('tipo_enfoque').addEventListener('change', function() {
    actualizarSubgrupos(this.value);
});

function actualizarSubgrupos(enfoque, seleccionActual = '') {
    const selectGrupo = document.getElementById('grupo_muscular');
    selectGrupo.innerHTML = '<option value="">Seleccione...</option>';

    if (enfoque === 'Musculo Individual') {
        const musculos = ['Cuádriceps', 'Glúteo', 'Bíceps', 'Tríceps', 'Pecho', 'Espalda', 'Hombro'];
        musculos.forEach(m => {
            selectGrupo.innerHTML += `<option value="${m}" ${m === seleccionActual ? 'selected' : ''}>${m}</option>`;
        });
    } else if (enfoque === 'Push-Pull-Legs') {
        const ppl = ['Push (Empuje)', 'Pull (Tirón)', 'Legs (Pierna)'];
        ppl.forEach(p => {
            selectGrupo.innerHTML += `<option value="${p}" ${p === seleccionActual ? 'selected' : ''}>${p}</option>`;
        });
    }
}

async function cargarRutinas() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        const tbody = document.getElementById('tablaRutinas');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center">No hay rutinas registradas.</td></tr>`;
            return;
        }

        data.forEach(r => {
            const fechaF = r.fecha_creacion ? r.fecha_creacion.split('T')[0] : '';
            tbody.innerHTML += `
                <tr>
                    <td>${r.id}</td>
                    <td>${r.nombre_rutina}</td>
                    <td><span class="badge bg-info text-dark">${r.tipo_enfoque}</span></td>
                    <td><b>${r.grupo_muscular}</b></td>
                    <td>${r.ejercicios}</td>
                    <td>${fechaF}</td>
                    <td>
                        <button class="btn btn-warning btn-sm mb-1" onclick='prepararEdicion(${JSON.stringify(r)})'>Editar</button>
                        <button class="btn btn-danger btn-sm mb-1" onclick="eliminarRutina(${r.id})">Eliminar</button>
                    </td>
                </tr>
            `;
        });
    } catch (error) { console.error("Error al cargar rutinas:", error); }
}

function prepararEdicion(r) {
    document.getElementById('editId').value = r.id;
    document.getElementById('nombre_rutina').value = r.nombre_rutina;
    document.getElementById('tipo_enfoque').value = r.tipo_enfoque;
    actualizarSubgrupos(r.tipo_enfoque, r.grupo_muscular);
    document.getElementById('ejercicios').value = r.ejercicios;
    document.getElementById('fecha_creacion').value = r.fecha_creacion ? r.fecha_creacion.split('T')[0] : '';
    
    document.getElementById('formTitle').innerText = "Editar Rutina #" + r.id;
    document.getElementById('btnGuardar').innerText = "Actualizar Rutina";
    document.getElementById('btnGuardar').className = "btn btn-warning w-100";
    document.getElementById('btnCancelar').classList.remove('d-none');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetFormulario() {
    document.getElementById('editId').value = '';
    document.getElementById('nombre_rutina').value = '';
    document.getElementById('tipo_enfoque').value = '';
    document.getElementById('grupo_muscular').innerHTML = '<option value="">Primero seleccione el enfoque...</option>';
    document.getElementById('ejercicios').value = '';
    document.getElementById('fecha_creacion').value = '';
    
    document.getElementById('formTitle').innerText = "Crear Nueva Rutina";
    document.getElementById('btnGuardar').innerText = "Guardar Rutina";
    document.getElementById('btnGuardar').className = "btn btn-success w-100";
    document.getElementById('btnCancelar').classList.add('d-none');
    document.getElementById('msg').innerHTML = '';
}

document.getElementById('btnGuardar').addEventListener('click', async () => {
    const id = document.getElementById('editId').value;
    const payload = {
        nombre_rutina: document.getElementById('nombre_rutina').value,
        tipo_enfoque: document.getElementById('tipo_enfoque').value,
        grupo_muscular: document.getElementById('grupo_muscular').value,
        ejercicios: document.getElementById('ejercicios').value,
        fecha_creacion: document.getElementById('fecha_creacion').value
    };

    if(!payload.nombre_rutina || !payload.tipo_enfoque || !payload.grupo_muscular || !payload.ejercicios || !payload.fecha_creacion) {
        document.getElementById('msg').innerHTML = '<div class="alert alert-warning">Por favor completa todos los campos.</div>';
        return;
    }

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/${id}` : API_URL;

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById('msg').innerHTML = `<div class="alert alert-success">¡Rutina ${id ? 'actualizada' : 'registrada'} con éxito!</div>`;
            resetFormulario();
            cargarRutinas();
        } else {
            document.getElementById('msg').innerHTML = '<div class="alert alert-danger">Error al procesar la solicitud.</div>';
        }
    } catch (error) { console.error("Error:", error); }
});

async function eliminarRutina(id) {
    if (!confirm("¿Seguro que deseas eliminar esta rutina?")) return;
    try {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (response.ok) cargarRutinas();
        else alert("Error al eliminar");
    } catch (error) { console.error("Error:", error); }
}

cargarRutinas();
</script>
</body>
</html>

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---

### 2. `routines_model.md`
```markdown
# Backend Model - Rutinas (routinesModel.js)
Ubicación en el servidor: `~/capasBack/src/models/routinesModel.js`

```javascript
const db = require('../config/db');

const Routines = {
    getAll: async () => {
        const [rows] = await db.query('SELECT * FROM routines');
        return rows;
    },
    create: async (data) => {
        const { nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion } = data;
        const [result] = await db.query(
            'INSERT INTO routines (nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion) VALUES (?, ?, ?, ?, ?)',
            [nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion]
        );
        return result;
    },
    update: async (id, data) => {
        const { nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion } = data;
        const [result] = await db.query(
            'UPDATE routines SET nombre_rutina=?, tipo_enfoque=?, grupo_muscular=?, ejercicios=?, fecha_creacion=? WHERE id=?',
            [nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion, id]
        );
        return result;
    },
    delete: async (id) => {
        const [result] = await db.query('DELETE FROM routines WHERE id=?', [id]);
        return result;
    }
};

module.exports = Routines;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---

### 3. `routines_controller.md`
```markdown
# Backend Controller - Rutinas (routinesController.js)
Ubicación en el servidor: `~/capasBack/src/controllers/routinesController.js`

```javascript
const express = require('express');
const router = express.Router();
const Routines = require('../models/routinesModel');

// GET: Obtener todas las rutinas
router.get('/', async (req, res) => {
    try {
        const routines = await Routines.getAll();
        res.json(routines);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// POST: Crear rutina
router.post('/', async (req, res) => {
    try {
        const result = await Routines.create(req.body);
        res.status(201).json({ message: 'Rutina creada', id: result.insertId });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// PUT: Actualizar rutina
router.put('/:id', async (req, res) => {
    try {
        await Routines.update(req.params.id, req.body);
        res.json({ message: 'Rutina actualizada' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// DELETE: Eliminar rutina
router.delete('/:id', async (req, res) => {
    try {
        await Routines.delete(req.params.id);
        res.json({ message: 'Rutina eliminada' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

---

### 4. `server_index.md`
```markdown
# Archivo Principal de Rutas y Servidor (index.js)
Ubicación en el servidor: `~/capasBack/src/index.js`

```javascript
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Importar las rutas del microservicio de rutinas
const routinesRoutes = require('./controllers/routinesController');

// Registrar los endpoints en la API central
app.use('/api/routines', routinesRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor corriendo en el puerto ${PORT}`);
});


------------------------------------------------------------------------------------------------------------------------------------

# Base de Datos y Estructura SQL - Rutinas
Motor: MySQL

```sql
-- 1. Crear la base de datos del taller (si no existe)
CREATE DATABASE IF NOT EXISTS fittrack_taller;

-- 2. Usar la base de datos
USE fittrack_taller;

-- 3. Crear la tabla de rutinas para el microservicio
CREATE TABLE IF NOT EXISTS routines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rutina VARCHAR(100) NOT NULL,
    tipo_enfoque VARCHAR(50) NOT NULL,
    grupo_muscular VARCHAR(50) NOT NULL,
    ejercicios TEXT NOT NULL,
    fecha_creacion DATE NOT NULL
);