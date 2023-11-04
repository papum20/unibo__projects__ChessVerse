#!/bin/bash

# down
docker compose -f $(ls docker-compose*.yml | awk '{printf "-f %s ", $0}') down