#!/bin/bash

# environment
set -a
source .env
source env/credentials.env

# volumes
mkdir -p ${VOLUME_MYSQL_DATA}

# start
docker compose $(ls docker-compose*.yml | awk '{printf "-f %s ", $0}') up -d