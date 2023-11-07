import os
import shutil
import subprocess


command1 = "python3.12 -m eel main.py web --name ChessVerse --icon=logo.png -w"
os.system(command1)



command2 = "create-dmg dist/Chessverse.App"
os.system(command2)


if not os.path.exists('versions'):
    os.makedirs('versions')


shutil.move('ChessVerse 0.0.0.dmg', 'versions/Chessverse_v1.0.dmg')
