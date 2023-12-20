# Usa l'immagine ufficiale di MySQL come base
FROM mysql:latest

EXPOSE 3306

# Imposta la password per l'utente root
ENV MYSQL_ROOT_PASSWORD='root'
ENV MYSQL_ROOT_HOST='%'

# Copia il file SQL di inizializzazione nella cartella /docker-entrypoint-initdb.d/
COPY ./data.sql /docker-entrypoint-initdb.d/

