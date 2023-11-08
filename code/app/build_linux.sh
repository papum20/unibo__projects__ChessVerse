#!/bin/bash

set -a
source ../../env/app.py

python3.12 -m eel main.py web --name ChessVerse --icon=logo.png -w
create-dmg dist/Chessverse.App

mkdir versions

mv ChessVerse 0.0.0.dmg versions/Chessverse_v1.0.dmg
