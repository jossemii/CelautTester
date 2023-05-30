FROM python:3.8

# Copiar todos los archivos de la raíz del proyecto al directorio de trabajo interno del contenedor
COPY . /app
WORKDIR /app

# Instalar las dependencias
RUN pip install grpcio==1.48.1 protobuf==3.19.4 grpcbigbuffer@git+https://github.com/jossemii/GRPCBigBuffer
