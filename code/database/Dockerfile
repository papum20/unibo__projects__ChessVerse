# Usa l'immagine ufficiale di MySQL come base
FROM mysql:latest

# Imposta la password per l'utente root
ENV MYSQL_ROOT_PASSWORD='root'

# Copia il file SQL di inizializzazione nella cartella /docker-entrypoint-initdb.d/
COPY create_db.sql /docker-entrypoint-initdb.d/
