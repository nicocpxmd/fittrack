# FitTrack
 
Aplicación de seguimiento y análisis de medidas corporales desarrollada con React, FastAPI y MongoDB Atlas.
 
## Tecnologías utilizadas
### Frontend
- React
- Vite
- JavaScript
 
### Backend
- Python
- FastAPI
- Uvicorn
 
### Base de datos
- MongoDB Atlas
 
---
 
## Clonar el repositorio
 
```bash
git clone https://github.com/nicocpxmd/fittrack.git
```
 
---
 
## Configuración del Backend
 
Ingresar a la carpeta backend:
 
```bash
cd backend
```
 
### Crear entorno virtual (solo la primera vez)
 
```bash
python -m venv venv
```
 
### Activar entorno virtual
  
```cmd
venv\Scripts\activate
```
 
### Instalar dependencias
 
```bash
pip install -r requirements.txt
```
 
### Variables de entorno
 
Crear un archivo `.env` utilizando como base el archivo `.env.example`.
 
Ejemplo:
 
```env
MONGODB_URL=
MONGODB_NAME=
```
 
### Ejecutar el backend
 
```bash
python -m uvicorn main:app --reload
```
 
Si todo está correcto, FastAPI se ejecutará en:
 
```text
http://127.0.0.1:8000
```
 
---
 
## Configuración del Frontend
 
Abrir una nueva terminal e ingresar a la carpeta frontend:
 
```bash
cd frontend
```
 
### Instalar dependencias
 
```bash
npm install
```
 
### Ejecutar aplicación
 
```bash
npm run dev
```
 
La aplicación estará disponible en una dirección similar a:
 
```text
http://localhost:5173
```
 
---
 
## Verificación de instalación
 
### Backend
 
Verificar que el servidor inicie sin errores:
 
```bash
python -m uvicorn main:app --reload
```
 
### Frontend
 
Verificar que Vite inicie correctamente:
 
```bash
npm run dev
```
 
Si ambos servicios se ejecutan correctamente, la instalación fue exitosa.

 
---
 
## Variables de entorno
 
Se proporciona un archivo `.env.example` como plantilla para la configuración local de cada integrante.

 
---
 
## Flujo de trabajo con Git
 
Actualizar repositorio:
 
```bash
git pull
```
 
Agregar cambios:
 
```bash
git add .
```
 
Crear commit:
 
```bash
git commit -m "Descripción del cambio"
```
 
Subir cambios:
 
```bash
git push
``` 
- No compartir credenciales de MongoDB en GitHub.
- No subir archivos `.env`.
- Utilizar el archivo `.env.example` como referencia para confige
