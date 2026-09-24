const mysql = require('mysql2/promise');

const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'goals',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

async function obtenerTodos() {
    const [rows] = await pool.query('SELECT * FROM goals ORDER BY created_at DESC');
    return rows;
}

async function obtenerPorId(id) {
    const [rows] = await pool.query('SELECT * FROM goals WHERE id = ?', [id]);
    return rows[0] || null;
}

async function obtenerPorUsuario(userId) {
    // Aquí userId ya vendrá como el UUID que provee el servicio de Users
    const [rows] = await pool.query('SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC', [userId]);
    return rows;
}

async function crear({ user_id, tipo_meta, descripcion, valor_objetivo, fecha_limite }) {
    const [result] = await pool.query(
        'INSERT INTO goals (user_id, tipo_meta, descripcion, valor_objetivo, fecha_limite) VALUES (?, ?, ?, ?, ?)',
        [user_id, tipo_meta, descripcion, valor_objetivo, fecha_limite]
    );
    return result.insertId;
}

async function actualizar(id, { user_id, tipo_meta, descripcion, valor_objetivo, fecha_limite }) {
    const [result] = await pool.query(
        'UPDATE goals SET user_id = ?, tipo_meta = ?, descripcion = ?, valor_objetivo = ?, fecha_limite = ? WHERE id = ?',
        [user_id, tipo_meta, descripcion, valor_objetivo, fecha_limite, id]
    );
    return result.affectedRows > 0;
}

async function eliminar(id) {
    const [result] = await pool.query('DELETE FROM goals WHERE id = ?', [id]);
    return result.affectedRows > 0;
}

module.exports = {
    obtenerTodos,
    obtenerPorId,
    obtenerPorUsuario,
    crear,
    actualizar,
    eliminar
};