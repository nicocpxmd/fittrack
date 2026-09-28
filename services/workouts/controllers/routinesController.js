const express = require('express');
const router = express.Router();
const Routines = require('../models/routinesModel');
const verificarUsuario = require('../middlewares/authMiddleware');

router.use(verificarUsuario); // todas las rutas de aquí en adelante requieren token válido

router.get('/', async (req, res) => {
    try {
        const routines = await Routines.getAllByUser(req.usuario.id);
        res.json(routines);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.post('/', async (req, res) => {
    try {
        const result = await Routines.create(req.usuario.id, req.body);
        res.status(201).json({ message: 'Rutina creada', id: result.insertId });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.put('/:id', async (req, res) => {
    try {
        const rutina = await Routines.getById(req.params.id);
        if (!rutina) return res.status(404).json({ error: 'Rutina no encontrada' });
        if (String(rutina.user_id) !== String(req.usuario.id)) {
            return res.status(403).json({ error: 'No tienes permiso para modificar esta rutina' });
        }
        await Routines.update(req.params.id, req.body);
        res.json({ message: 'Rutina actualizada' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.delete('/:id', async (req, res) => {
    try {
        const rutina = await Routines.getById(req.params.id);
        if (!rutina) return res.status(404).json({ error: 'Rutina no encontrada' });
        if (String(rutina.user_id) !== String(req.usuario.id)) {
            return res.status(403).json({ error: 'No tienes permiso para eliminar esta rutina' });
        }
        await Routines.delete(req.params.id);
        res.json({ message: 'Rutina eliminada' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
