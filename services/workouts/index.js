require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Importar las rutas de rutinas
const routinesRoutes = require('./controllers/routinesController');
app.use('/api/routines', routinesRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor de Rutinas corriendo en el puerto ${PORT}`);
});