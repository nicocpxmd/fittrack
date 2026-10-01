const { Router } = require('express');
const axios = require('axios');
const goalsModel = require('../models/goalsModel');
const verificarUsuario = require('../middlewares/authMiddleware');
const router = Router();

router.use(verificarUsuario); // todas las rutas de Goals requieren token válido

async function calcularProgresoActual(goal, token) {
    const progressUrl = process.env.PROGRESS_SERVICE_URL || 'http://192.168.100.3:8005';
    const fechaInicio = '1970-01-01'; // solo interesa la medida más reciente
    const fechaFin = new Date().toISOString().slice(0, 10);

    try {
        const response = await axios.post(
            `${progressUrl}/progress/calculate`,
            { tipo_medida: goal.tipo_meta, desde: fechaInicio, hasta: fechaFin },
            { headers: { Authorization: token }, timeout: 5000 }
        );

        if (response.data && response.data.valor_actual != null) {
            return {
		valorActual: Number(response.data.valor_actual),
		valorInicial: response.data.valor_inicial != null ? Number(response.data.valor_inicial) : null
	   };
        }
        throw new Error('El servicio progress devolvió una respuesta sin valor_actual.');
    } catch (progressError) {
        console.warn(`[Goals] No se pudo obtener el progreso desde progress: ${progressError.message}`);
        const detail = progressError.response?.data?.detail;
        if (
            progressError.response?.status === 404 &&
            typeof detail === 'string' &&
            detail.startsWith('No measurements found for type ')
        ) {
            return null;
        }
        if (progressError.response?.status === 401) {
            const authError = new Error('El token no fue aceptado por progress.');
            authError.statusCode = 401;
            throw authError;
        }
        const upstreamError = new Error('No se pudo obtener el progreso desde el servicio progress.');
        upstreamError.statusCode = 502;
        throw upstreamError;
    }
}

// CREATE
router.post('/goals', async (req, res) => {
    try {
        const { tipo_meta, descripcion, valor_objetivo, fecha_limite } = req.body;
        if (!tipo_meta || !descripcion || !valor_objetivo || !fecha_limite) {
            return res.status(400).json({ error: "Faltan datos obligatorios para crear la meta." });
        }
        const newId = await goalsModel.crear({
            user_id: req.usuario.id,
            tipo_meta,
            descripcion,
            valor_objetivo,
            fecha_limite,
            direccion: ['subir', 'bajar'].includes(req.body.direccion) ? req.body.direccion : 'subir'
        });
        res.status(201).json({ mensaje: "Meta creada exitosamente", id: newId });
    } catch (error) {
        console.error("Error al registrar:", error);
        res.status(500).json({ error: "Error interno del servidor." });
    }
});

// READ ALL — solo las metas del usuario autenticado
router.get('/goals', async (req, res) => {
    try {
        const metas = await goalsModel.obtenerPorUsuario(req.usuario.id);
        res.status(200).json(metas);
    } catch (error) {
        res.status(500).json({ error: "Error al consultar metas." });
    }
});

// GET /goals/admin/all — ver nota abajo, queda pendiente de tu decisión
router.get('/goals/admin/all', async (req, res) => {
    try {
        const todasLasMetas = await goalsModel.obtenerTodos();
        res.status(200).json(todasLasMetas);
    } catch (error) {
        console.error("Error al obtener todas las metas:", error);
        res.status(500).json({ error: "Error al obtener todas las metas." });
    }
});

// READ ONE — recalcula y persiste el progreso
router.get('/goals/:id', async (req, res) => {
    try {
        const meta = await goalsModel.obtenerPorId(req.params.id);
        if (!meta) {
            return res.status(404).json({ error: "Meta no encontrada." });
        }
        if (String(meta.user_id) !== String(req.usuario.id)) {
            return res.status(403).json({ error: "La meta no pertenece al usuario autenticado." });
        }

        const resultado = await calcularProgresoActual(meta, req.token);
        if (resultado === null) {
            return res.status(200).json({ ...meta, sin_medidas: true });
        }
        const objetivo = Number(meta.valor_objetivo);
	const valorActual = resultado.valorActual;
        const inicial = meta.valor_inicial != null ? Number(meta.valor_inicial) : resultado.valorInicial;
        const bajar = meta.direccion === 'bajar';
        const cumplida = bajar ? valorActual <= objetivo : valorActual >= objetivo;
        const recorrido = bajar ? inicial - valorActual : valorActual - inicial;
        const total = bajar ? inicial - objetivo : objetivo - inicial;
        const porcentajeCumplimiento = cumplida
            ? 100
            : total > 0 ? Math.max(0, Math.min(100, Number(((recorrido / total) * 100).toFixed(2)))) : 0;

        await goalsModel.actualizarProgreso(meta.id, {
            valor_actual: valorActual,
            porcentaje_cumplimiento: porcentajeCumplimiento,
            cumplida,
            valor_inicial: inicial
        });

        res.status(200).json({ ...meta, valor_actual: valorActual, porcentaje_cumplimiento: porcentajeCumplimiento, cumplida });
    } catch (error) {
        console.error("Error al procesar la meta:", error);
        if (error.statusCode) {
            return res.status(error.statusCode).json({ error: error.message });
        }
        res.status(500).json({ error: "Error interno al procesar la solicitud." });
    }
});

// UPDATE
router.put('/goals/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const metaExistente = await goalsModel.obtenerPorId(id);
        if (!metaExistente) {
            return res.status(404).json({ error: "La meta especificada no existe." });
        }
        if (String(metaExistente.user_id) !== String(req.usuario.id)) {
            return res.status(403).json({ error: "No tienes permiso para modificar esta meta." });
        }

        const datosActualizados = {
            user_id: metaExistente.user_id,
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

// DELETE
router.delete('/goals/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const metaExistente = await goalsModel.obtenerPorId(id);
        if (!metaExistente) {
            return res.status(404).json({ error: "No se encontró la meta a eliminar." });
        }
        if (String(metaExistente.user_id) !== String(req.usuario.id)) {
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
