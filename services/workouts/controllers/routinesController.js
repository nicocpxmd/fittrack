const express = require('express');
const router = express.Router();
const Routines = require('../models/routinesModel');
const verificarUsuario = require('../middlewares/authMiddleware');

// GET: pública (no requiere validar usuario)
router.get('/', async (req, res) => {
    try {
        const routines = await Routines.getAll();
        res.json(routines);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// POST: requiere usuario autenticado en el microservicio Users
router.post('/', verificarUsuario, async (req, res) => {
    try {
        const result = await Routines.create(req.body);
        res.status(201).json({
            message: 'Rutina creada',
            id: result.insertId,
            creada_por: req.usuario.email
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.put('/:id', verificarUsuario, async (req, res) => {
    try {
        await Routines.update(req.params.id, req.body);
        res.json({ message: 'Rutina actualizada' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

router.delete('/:id', verificarUsuario, async (req, res) => {
    try {
        await Routines.delete(req.params.id);
        res.json({ message: 'Rutina eliminada' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;