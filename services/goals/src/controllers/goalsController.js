const { Router } = require('express');
const axios = require('axios');
const goalsModel = require('../models/goalsModel');

const router = Router();

// Función auxiliar para extraer el token JWT de la petición del frontend
function extraerToken(req) {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
        return authHeader.split(' ')[1];
    }
    return null;
}

// 1. VALIDACIÓN CROSS-SERVICE: Llama a GET /users/me enviando el token
async function obtenerUsuarioAutenticado(token) {
    if (!token) throw new Error("No token provided");
    
    const usersUrl = process.env.USERS_SERVICE_URL || 'http://localhost:8002';
    try {
        const response = await axios.get(`${usersUrl}/users/me`, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 3000
        });
        return response.data; // Retorna el usuario autenticado (con su id)
    } catch (error) {
        throw new Error("No se pudo validar el usuario con el servicio Users");
    }
}

async function calcularProgresoActual(goal) {
    let valorActual = 0;
    try {
        if (goal.tipo_meta === 'rutina') {
            // Consumimos la ruta real que existe en el microservicio de rutinas: GET /api/routines
            const workoutsUrl = process.env.WORKOUTS_SERVICE_URL || 'http://localhost:8003';
            const response = await axios.get(`${workoutsUrl}/api/routines`, { timeout: 3000 });
            
            const rutinas = response.data; // Esto es un array con las rutinas
            
            valorActual = Array.isArray(rutinas) ? rutinas.length : 0;

        } else {
            // Si la meta es de medida corporal (ej. weight_kg), consultamos a Progress
            const progressUrl = process.env.PROGRESS_SERVICE_URL || 'http://localhost:8005';
            const response = await axios.get(`${progressUrl}/progress/${goal.user_id}`, { timeout: 3000 });
            
            const snapshots = response.data;
            const snapshotMedida = snapshots.find(p => p.tipo_medida === goal.tipo_meta);
            
            if (snapshotMedida) {
                valorActual = snapshotMedida.valor_actual;
            }
        }
    } catch (error) {
        console.warn(`[Goals] No se pudo obtener el progreso externo: ${error.message}`);
    }
    return valorActual;
}

// ==========================================
// CRUD COMPLETO
// ==========================================

// CREATE (POST /goals)
router.post('/goals', async (req, res) => {
    try {
        const token = extraerToken(req);
        let usuario;
        
        try {
            usuario = await obtenerUsuarioAutenticado(token);
        } catch (err) {
            return res.status(401).json({ error: "No autorizado. Token inválido o expirado." });
        }

        const { tipo_meta, descripcion, valor_objetivo, fecha_limite } = req.body;
        if (!tipo_meta || !descripcion || !valor_objetivo || !fecha_limite) {
            return res.status(400).json({ error: "Faltan datos obligatorios para crear la meta." });
        }

        const newId = await goalsModel.crear({ 
            user_id: usuario.id, 
            tipo_meta, 
            descripcion, 
            valor_objetivo, 
            fecha_limite 
        });
        
        res.status(201).json({ mensaje: "Meta creada exitosamente", id: newId });

    } catch (error) {
        console.error("Error al registrar:", error);
        res.status(500).json({ error: "Error interno del servidor." });
    }
});

// READ ALL (GET /goals) - Devuelve las metas del usuario autenticado
router.get('/goals', async (req, res) => {
    try {
        const token = extraerToken(req);
        const usuario = await obtenerUsuarioAutenticado(token);

        const metas = await goalsModel.obtenerPorUsuario(usuario.id);
        res.status(200).json(metas);
    } catch (error) {
        res.status(401).json({ error: "No autorizado o error al consultar metas." });
    }
});

// READ ONE (GET /goals/:id) - Trae una meta calculando su progreso actual
router.get('/goals/:id', async (req, res) => {
    try {
        const meta = await goalsModel.obtenerPorId(req.params.id);
        if (!meta) {
            return res.status(404).json({ error: "Meta no encontrada." });
        }

        const valorActual = await calcularProgresoActual(meta);
        const porcentajeCumplimiento = Math.min(100, Number(((valorActual / meta.valor_objetivo) * 100).toFixed(2)));

        res.status(200).json({
            ...meta,
            valor_actual: valorActual,
            porcentaje_cumplimiento: porcentajeCumplimiento,
            cumplida: valorActual >= meta.valor_objetivo
        });
    } catch (error) {
        res.status(500).json({ error: "Error interno al procesar la solicitud." });
    }
});

// UPDATE (PUT /goals/:id) - Actualiza los datos de una meta existente
router.put('/goals/:id', async (req, res) => {
    try {
        const token = extraerToken(req);
        let usuario;
        try {
            usuario = await obtenerUsuarioAutenticado(token);
        } catch (err) {
            return res.status(401).json({ error: "No autorizado." });
        }

        const { id } = req.params;
        const metaExistente = await goalsModel.obtenerPorId(id);

        if (!metaExistente) {
            return res.status(404).json({ error: "La meta especificada no existe." });
        }

        // Seguridad: Verificar que la meta pertenezca al usuario autenticado
        if (metaExistente.user_id !== usuario.id) {
            return res.status(403).json({ error: "No tienes permiso para modificar esta meta." });
        }

        const datosActualizados = {
            user_id: usuario.id,
            tipo_meta: req.body.tipo_meta || metaExistente.tipo_meta,
            descripcion: req.body.descripcion || metaExistente.descripcion,
            valor_objetivo: req.body.valor_objetivo || metaExistente.valor_objetivo,
            fecha_limite: req.body.fecha_limite || metaExistente.fecha_limite
        };

        await goalsModel.actualizar(id, datosActualizados);
        res.status(200).json({ mensaje: "Meta actualizada exitosamente." });

    } catch (error) {
        console.error("Error al actualizar la meta:", error);
        res.status(500).json({ error: "Error interno del servidor." });
    }
});

// DELETE (DELETE /goals/:id) - Elimina una meta por su ID
router.delete('/goals/:id', async (req, res) => {
    try {
        const token = extraerToken(req);
        let usuario;
        try {
            usuario = await obtenerUsuarioAutenticado(token);
        } catch (err) {
            return res.status(401).json({ error: "No autorizado." });
        }

        const { id } = req.params;
        const metaExistente = await goalsModel.obtenerPorId(id);

        if (!metaExistente) {
            return res.status(404).json({ error: "No se encontró la meta a eliminar." });
        }

        // Seguridad: Verificar que la meta pertenezca al usuario autenticado
        if (metaExistente.user_id !== usuario.id) {
            return res.status(403).json({ error: "No tienes permiso para eliminar esta meta." });
        }

        await goalsModel.eliminar(id);
        res.status(200).json({ mensaje: "Meta eliminada correctamente." });

    } catch (error) {
        console.error("Error al eliminar la meta:", error);
        res.status(500).json({ error: "Error interno del servidor." });
    }
});

module.exports = router;