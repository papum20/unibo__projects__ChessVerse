#!/bin/bash

REMOTE_USER="kekko"
REMOTE_HOST="chessverse.germanywestcentral.cloudapp.azure.com"
REMOTE_DIR="~/t4-chessverse"

# Connessione SSH e esecuzione dei comandi
ssh $REMOTE_USER@$REMOTE_HOST << EOF
  cd $REMOTE_DIR
  git pull
  sudo docker-compose build
  sudo docker-compose up -d
EOF