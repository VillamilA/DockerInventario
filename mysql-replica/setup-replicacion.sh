#!/bin/bash

# Crear red
docker network create red-replicacion

# Crear volúmenes
docker volume create vol-master
docker volume create vol-slave

# Crear contenedor maestro
docker run -d --name db-master \
  -v vol-master:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  --network red-replicacion \
  -p 3306:3306 \
  mysql:5.7

# Crear contenedor esclavo
docker run -d --name db-slave \
  -v vol-slave:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  --network red-replicacion \
  -p 3307:3306 \
  mysql:5.7

# Esperar a que arranquen
echo "Esperando 15s para que arranquen los contenedores..."
sleep 15

# Copiar configuraciones
docker cp master.cnf db-master:/etc/mysql/my.cnf
docker cp slave.cnf db-slave:/etc/mysql/my.cnf

# Reiniciar contenedores
docker restart db-master
docker restart db-slave

echo "Contenedores reiniciados con configuración aplicada."
