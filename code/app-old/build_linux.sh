#!/bin/bash

set -a
source ../../env/app.env

python3 -m eel main.py web --name ChessVerse --icon=logo.png -w

zip -r chessverse_debian.zip dist/ChessVerse