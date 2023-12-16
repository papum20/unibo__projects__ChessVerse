#!/bin/bash

# Imposta valori di default
default_server_address="localhost"
default_server_port="3306"
default_user="root"
root_password="root"  # Password target per l'utente 'root'

# Richiedi i dettagli di connessione al server MySQL con valori di default
read -p "Inserisci l'indirizzo del server MySQL [$default_server_address]: " server_address
server_address=${server_address:-$default_server_address}

read -p "Inserisci la porta del server MySQL [$default_server_port]: " server_port
server_port=${server_port:-$default_server_port}

read -p "Inserisci l'username per il server MySQL [$default_user]: " mysql_username
mysql_username=${mysql_username:-$default_user}

read -s -p "Inserisci la password per il server MySQL: " mysql_password
echo

# Comando per connettersi a MySQL
MYSQL_CMD="mysql -h $server_address -P $server_port -u $mysql_username -p$mysql_password"

# Verifica l'esistenza dell'utente 'root' e lo crea se non esiste
echo "Verifica dell'esistenza dell'utente 'root'..."
if ! $MYSQL_CMD -e "SELECT 1 FROM mysql.user WHERE user = 'root'" >/dev/null 2>&1; then
    echo "L'utente 'root' non esiste. Creazione in corso..."
    $MYSQL_CMD -e "CREATE USER 'root'@'%' IDENTIFIED BY '$root_password';"
    $MYSQL_CMD -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"
    $MYSQL_CMD -e "FLUSH PRIVILEGES;"
fi

# Cambia la password dell'utente 'root' con mysqladmin
echo "Aggiornamento della password per l'utente 'root' con mysqladmin..."
MYSQLADMIN_CMD="mysqladmin -h $server_address -P $server_port -u root -p$mysql_password password $root_password"
if $MYSQLADMIN_CMD 2>/dev/null; then
    echo "Password dell'utente 'root' cambiata con successo."
else
    echo "Errore nel cambiamento della password. Verifica i permessi o i dettagli di connessione."
fi

# Crea il database 'users_db' se non esiste
echo "Creazione del database 'users_db'..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS users_db;"

# Funzione per copiare i dati da un database all'altro
copy_database() {
    local source_db=$1
    local target_db=$2

    # Verifica che il database sorgente esista
    if $MYSQL_CMD -e "USE $source_db;" 2>/dev/null; then
        echo "Copia del database $source_db in $target_db..."
        # Copia ogni tabella dal database sorgente al database di destinazione
        tables=$($MYSQL_CMD -e "SHOW TABLES;" -s --skip-column-names -D $source_db)
        for table in $tables; do
            $MYSQL_CMD -e "CREATE TABLE IF NOT EXISTS $target_db.$table LIKE $source_db.$table;"
            $MYSQL_CMD -e "INSERT INTO $target_db.$table SELECT * FROM $source_db.$table;"
        done
        echo "Copia completata."
    else
        echo "Database $source_db non trovato."
    fi
}

# Chiedi all'utente se desidera copiare i dati da un altro database
read -p "Caricare users_db da un altro database? [y/N]: " copy_db_decision
if [[ $copy_db_decision == [yY] ]]; then
    read -p "Inserisci il nome del database da copiare in users_db: " source_db_name
    if [[ ! -z $source_db_name ]]; then
        copy_database $source_db_name "users_db"
    fi
fi

echo "Operazioni completate."

