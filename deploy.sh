#!/bin/bash

REMOTE_USER="prod"
REMOTE_HOST="chessverse.northeurope.cloudapp.azure.com"
REMOTE_DIR="/home/prod/t4-chessverse"

# Connessione SSH e esecuzione dei comandi
ssh $REMOTE_USER@$REMOTE_HOST << EOF
  cd $REMOTE_DIR
  git checkout origin/prod
  git pull
  docker rm $(docker ps -a -q)
  docker compose build
  docker compose up -d
EOF
