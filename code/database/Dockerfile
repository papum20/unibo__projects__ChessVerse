# Usa l'immagine ufficiale di MySQL come base
FROM mysql:latest

EXPOSE 3306

# Imposta la password per l'utente root
ENV MYSQL_ROOT_PASSWORD='root'
ENV MYSQL_ROOT_HOST='%'

RUN apt-get update -y && apt-get install gcc pkg-config -y && apt-get clean 
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential -y && apt-get install mysql-community-server && apt-get install mysql-community-client && apt-get clean

# Copia il file SQL di inizializzazione nella cartella /docker-entrypoint-initdb.d/
COPY ./data.sql /docker-entrypoint-initdb.d/

