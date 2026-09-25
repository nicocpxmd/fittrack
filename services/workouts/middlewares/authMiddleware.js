const axios = require('axios');

async function verificarUsuario(req, res, next) {
    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'Falta el token de autorización' });
    }

    try {
        const response = await axios.get(`${process.env.USERS_SERVICE_URL}/users/me`, {
            headers: { Authorization: token }
        });
        req.usuario = response.data; // guardamos el usuario validado para usarlo si hace falta
        next();
    } catch (error) {
        res.status(401).json({ error: 'Token inválido o el servicio Users no respondió' });
    }
}

module.exports = verificarUsuario;