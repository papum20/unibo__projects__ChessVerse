#!/bin/bash

# down
docker compose $(ls docker-compose*.yml | awk '{printf "-f %s ", $0}') down