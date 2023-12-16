#!/bin/bash

SSH_NAME="azure_prod"
REMOTE_DIR="/home/prod/t4-chessverse"

# Connessione SSH e esecuzione dei comandi; azure_prod configurato da setup.sh
ssh $SSH_NAME << EOF
  cd $REMOTE_DIR
  git checkout origin/prod
  git pull
  docker rm $(docker ps -a -q)
  sudo docker compose build
  docker compose up -d
EOF
