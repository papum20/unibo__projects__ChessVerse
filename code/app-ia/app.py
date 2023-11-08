from flask import Flask, Blueprint, render_template, redirect, request, session, url_for
import chess
import os

app = Flask(__name__)
app.secret_key = 'your secret key'  # replace with your secret key
webapp = Blueprint(os.getenv('SUBPATH', '/'), __name__)

def print_board(board):
    rows = board.__str__().split("\n")
    result = []
    for i in range(len(rows)):
        result.append(f"{8-i} {rows[i]}")
    result.append("  a b c d e f g h")
    return "\n".join(result)

@webapp.route('/')
def index():
    fen = session.get('fen', chess.STARTING_FEN)
    board = chess.Board(fen)
    return render_template('index.html', board=print_board(board), fen=fen)

@webapp.route('/move', methods=['POST'])
def move():
    uci_move = request.form.get('move')
    fen = session.get('fen', chess.STARTING_FEN)
    board = chess.Board(fen)
    if chess.Move.from_uci(uci_move) in board.legal_moves:
        board.push_uci(uci_move)
        session['fen'] = board.fen()
    else:
        return "Illegal move. Try again.", 400
    return redirect(url_for('/webapp.index'))

app.register_blueprint(webapp, url_prefix=os.getenv('SUBPATH', '/'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)) )