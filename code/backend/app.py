from flask import Flask, Blueprint, send_file
import os

app = Flask(__name__)
app.secret_key = 'your secret key'  # replace with your secret key
api = Blueprint(os.getenv('SUBPATH', '/'), __name__)

app = Flask(__name__)

@api.route('/download/macos_latest', methods=['GET'])
def download():
    file_path = os.path.join(os.getenv('PATH_RELEASES'), 'chessverse1_0_0-macos.dmg')
    return send_file(file_path, as_attachment=True)

@api.route('/download/windows11_latest', methods=['GET'])
def download2():
    file_path = os.path.join(os.getenv('PATH_RELEASES'), 'chessverse1_0_0-windows11.exe')
    return send_file(file_path, as_attachment=True)

@api.route('/download/debian_latest', methods=['GET'])
def download3():
    file_path = os.path.join(os.getenv('PATH_RELEASES'), 'chessverse_debian.zip')
    #file_path = os.path.join(os.getenv('PATH_RELEASES'), 'chessverse1_0_0-debian.exe')
    return send_file(file_path, as_attachment=True)

app.register_blueprint(api, url_prefix=os.getenv('SUBPATH', '/'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)) )
