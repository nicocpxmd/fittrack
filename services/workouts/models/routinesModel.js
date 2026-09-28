const db = require('../config/db');

const Routines = {
    getAllByUser: async (userId) => {
        const [rows] = await db.query('SELECT * FROM routines WHERE user_id = ?', [userId]);
        return rows;
    },
    create: async (userId, data) => {
        const { nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion } = data;
        const [result] = await db.query(
            'INSERT INTO routines (user_id, nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?)',
            [userId, nombre_rutina, tipo_enfoque, grupo_muscular, ejercicios, fecha_creacion]
        );
        return result;
    },
    getById: async (id) => {
        const [rows] = await db.query('SELECT * FROM routines WHERE id = ?', [id]);
        return rows[0] || null;
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
