#!/bin/bash

# environment
set -a
source .env
source env/credentials.env

envsubst < code/app/.env.example > code/app/.env

# volumes
mkdir -p ${VOLUME_MYSQL_DATA}

# start
docker compose $(ls docker-compose*.yml | awk '{printf "-f %s ", $0}') build
docker compose $(ls docker-compose*.yml | awk '{printf "-f %s ", $0}') up -d