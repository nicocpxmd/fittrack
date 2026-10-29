FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY generar_dataset.py validar_dataset.py ./

# Por defecto genera el dataset en /data (montar una carpeta del anfitrion ahi).
ENTRYPOINT ["python"]
CMD ["generar_dataset.py", "--salida", "/data"]
