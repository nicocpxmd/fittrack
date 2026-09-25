const { Router } = require('express');
const axios = require('axios');
const goalsModel = require('../models/goalsModel');

const router = Router();

async function calcularProgresoActual(goal) {
    let valorActual = 0;
    try {
        if (goal.tipo_meta === 'rutina') {
            const workoutsUrl = process.env.WORKOUTS_SERVICE_URL || 'http://localhost:8003';
            const response = await axios.get(`${workoutsUrl}/api/routines`, { timeout: 3000 });
            const rutinas = response.data;
            valorActual = Array.isArray(rutinas) ? rutinas.length : 0;

        } else {
            const progressUrl = process.env.PROGRESS_SERVICE_URL || 'http://localhost:8006';
            const fechaInicio = goal.created_at
                ? new Date(goal.created_at).toISOString().slice(0, 10)
                : '1970-01-01';
            const fechaFin = new Date().toISOString().slice(0, 10);

            try {
                const response = await axios.post(`${progressUrl}/progress/calculate`, {
                    user_id: String(goal.user_id),
                    tipo_medida: goal.tipo_meta,
                    desde: fechaInicio,
                    hasta: fechaFin
                }, { timeout: 5000 });

                if (response.data && response.data.valor_actual != null) {
                    return Number(response.data.valor_actual);
                }
            } catch (progressError) {
                console.warn(`[Goals] Progress no disponible, usando measurements: ${progressError.message}`);
            }

            const measurementsUrl = process.env.MEASUREMENTS_SERVICE_URL || 'http://localhost:8005';
            const response = await axios.get(`${measurementsUrl}/measurements/`, { timeout: 3000 });
            let registros = response.data;

            if (registros && !Array.isArray(registros)) {
                registros = Array.isArray(registros.data) ? registros.data : [registros];
            }

            if (Array.isArray(registros)) {
                for (let i = registros.length - 1; i >= 0; i--) {
                    const registro = registros[i];
                    if (registro.measurements && registro.measurements[goal.tipo_meta] != null) {
                        valorActual = registro.measurements[goal.tipo_meta];
                        break;
                    }
                }
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
        const { user_id, tipo_meta, descripcion, valor_objetivo, fecha_limite } = req.body;
        if (!user_id || !tipo_meta || !descripcion || !valor_objetivo || !fecha_limite) {
            return res.status(400).json({ error: "Faltan datos obligatorios para crear la meta." });
        }

        const newId = await goalsModel.crear({ 
            user_id,
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
        const { user_id } = req.query;
        if (!user_id) {
            return res.status(400).json({ error: "user_id es obligatorio." });
        }

        const metas = await goalsModel.obtenerPorUsuario(user_id);
        res.status(200).json(metas);
    } catch (error) {
        res.status(500).json({ error: "Error al consultar metas." });
    }
});

// GET /goals/admin/all (Global y sin filtrar)
router.get('/goals/admin/all', async (req, res) => {
    try {
        const todasLasMetas = await goalsModel.obtenerTodos(); 
        res.status(200).json(todasLasMetas);
    } catch (error) {
        console.error("Error al obtener todas las metas:", error);
        res.status(500).json({ error: "Error al obtener todas las metas." });
    }
});

// READ ONE (GET /goals/:id) - Trae una meta calculando su progreso actual
router.get('/goals/:id', async (req, res) => {
    try {
        const { user_id } = req.query;
        if (!user_id) {
            return res.status(400).json({ error: "user_id es obligatorio." });
        }

        const meta = await goalsModel.obtenerPorId(req.params.id);
        if (!meta) {
            return res.status(404).json({ error: "Meta no encontrada." });
        }
        if (String(meta.user_id) !== String(user_id)) {
            return res.status(403).json({ error: "La meta no pertenece al usuario indicado." });
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
        const { id } = req.params;
        const { user_id } = req.body;
        if (!user_id) {
            return res.status(400).json({ error: "user_id es obligatorio." });
        }

        const metaExistente = await goalsModel.obtenerPorId(id);

        if (!metaExistente) {
            return res.status(404).json({ error: "La meta especificada no existe." });
        }

        if (String(metaExistente.user_id) !== String(user_id)) {
            return res.status(403).json({ error: "No tienes permiso para modificar esta meta." });
        }

        const datosActualizados = {
            user_id,
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
        const { id } = req.params;
        const { user_id } = req.query;
        if (!user_id) {
            return res.status(400).json({ error: "user_id es obligatorio." });
        }

        const metaExistente = await goalsModel.obtenerPorId(id);

        if (!metaExistente) {
            return res.status(404).json({ error: "No se encontró la meta a eliminar." });
        }

        if (String(metaExistente.user_id) !== String(user_id)) {
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