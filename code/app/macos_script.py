import os
import shutil
import subprocess

# Eseguire il comando per avviare il server Eel
command1 = "python3.12 -m eel main.py web --name ChessVerse --icon=logo.png -w"
os.system(command1)


# Eseguire il comando per creare il file DMG
command2 = "create-dmg dist/Chessverse.App"
os.system(command2)

# Creare la cartella 'versions' se non esiste già
if not os.path.exists('versions'):
    os.makedirs('versions')

# Spostare il file DMG creato nella cartella 'versions'
shutil.move('ChessVerse 0.0.0.dmg', 'versions/Chessverse_v1.0.dmg')
