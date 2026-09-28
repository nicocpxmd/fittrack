// services/goals/src/middlewares/authMiddleware.js
const axios = require('axios');

async function verificarUsuario(req, res, next) {
    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'Falta el token de autorización' });
    }
    try {
        const usersUrl = process.env.USERS_SERVICE_URL || 'http://192.168.100.3:8002';
        const response = await axios.get(`${usersUrl}/users/me`, {
            headers: { Authorization: token }
        });
        req.usuario = response.data;
        req.token = token; // se reenvía a Progress
        next();
    } catch (error) {
        res.status(401).json({ error: 'Token inválido o el servicio Users no respondió' });
    }
}

module.exports = verificarUsuario;
