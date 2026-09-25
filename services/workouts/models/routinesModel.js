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