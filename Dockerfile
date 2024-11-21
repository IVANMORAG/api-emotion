# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt /app/

# Copia el archivo de requisitos
COPY requirements.txt /app/

# Instala las dependencias
RUN pip install --no-cache-dir --default-timeout=1000 -r /app/requirements.txt

# Copia todos los archivos de la aplicación al contenedor
COPY . /app/

# Expone el puerto en el que Flask escucha (por defecto 5000)
EXPOSE 5000

# Usa el comando de ejecución adecuado para la aplicación Flask
ENTRYPOINT ["python", "app.py"]