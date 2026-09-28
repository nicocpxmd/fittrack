require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const swaggerUi = require('swagger-ui-express');
const openapiSpec = require('./openapi.json');

const app = express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Swagger UI (equivalente al /docs que trae FastAPI en los servicios Python)
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openapiSpec));

// Importar las rutas de rutinas
const routinesRoutes = require('./controllers/routinesController');
app.use('/api/routines', routinesRoutes);

const PORT = process.env.PORT || 8003;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor de Rutinas corriendo en el puerto ${PORT}`);
    console.log(`Swagger disponible en http://localhost:${PORT}/api-docs`);
});
