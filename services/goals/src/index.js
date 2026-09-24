require('dotenv').config();
const express = require('express');
const morgan = require('morgan');
const cors = require('cors');
const goalsController = require('./controllers/goalsController');

const app = express();

// Middlewares globales
app.use(morgan('dev'));
app.use(cors());
app.use(express.json());

// Montaje de las rutas del controlador de Goals
// (Como el controlador define rutas como '/goals', aquí se montan directamente)
app.use(goalsController);

// Puerto del microservicio (por defecto 8004 según la arquitectura del equipo)
const PORT = process.env.GOALS_PORT || 8004;

app.listen(PORT, () => {
    console.log(`[FitTrack] Microservicio Goals ejecutándose en el puerto ${PORT}`);
});