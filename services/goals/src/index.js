require('dotenv').config();
const express = require('express');
const morgan = require('morgan');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const openapiSpec = require('../openapi.json');
const goalsController = require('./controllers/goalsControllers');

const app = express();

// Middlewares globales
app.use(morgan('dev'));
app.use(cors());
app.use(express.json());

// Swagger UI (equivalente al /docs que trae FastAPI en los servicios Python)
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openapiSpec));

// Montaje de las rutas del controlador de Goals
app.use(goalsController);

// Puerto del microservicio (por defecto 8004 según la arquitectura del equipo)
const PORT = process.env.GOALS_PORT || 8004;
app.listen(PORT, () => {
    console.log(`[FitTrack] Microservicio Goals ejecutándose en el puerto ${PORT}`);
    console.log(`Swagger disponible en http://localhost:${PORT}/api-docs`);
});
