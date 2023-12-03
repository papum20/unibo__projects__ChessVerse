#!/bin/bash

CREDENTIALS_LENGTH_USER=8
CREDENTIALS_LENGTH_PASSWORD=16
CREDENTIALS_FILE_NAME=${PWD}/env/credentials.env

replace_random() {
    local length=$1
    tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w "$length" | head -n 1
}


if [ -f "$CREDENTIALS_FILE_NAME" ]; then
    echo "Error: File $CREDENTIALS_FILE_NAME already exists, you would overwrite and lose old credentials.
    please remove the file manually."
else
    echo "File $CREDENTIALS_FILE_NAME doesn't exist, creating..."

    cat > env/credentials.env <<EOF
CHESSVERSE_MYSQL_ROOT_PASSWORD=$(replace_random $CREDENTIALS_LENGTH_PASSWORD)
CHESSVERSE_MYSQL_USER=$(replace_random $CREDENTIALS_LENGTH_USER)
CHESSVERSE_MYSQL_PASSWORD=$(replace_random $CREDENTIALS_LENGTH_PASSWORD)
EOF

fi
