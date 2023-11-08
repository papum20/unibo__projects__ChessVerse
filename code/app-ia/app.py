from flask import Flask, Blueprint, render_template, request
import chess
import os

app = Flask(__name__)
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
    board = chess.Board()
    return render_template('index.html', board=print_board(board))
@webapp.route('/webapp/')
def index():
    board = chess.Board()
    return render_template('index.html', board=print_board(board))

@webapp.route('/move', methods=['POST'])
def move():
    uci_move = request.form.get('move')
    board = chess.Board(request.form.get('board'))
    if chess.Move.from_uci(uci_move) in board.legal_moves:
        board.push_uci(uci_move)
    else:
        return "Illegal move. Try again.", 400
    return print_board(board)

app.register_blueprint(webapp, url_prefix=os.getenv('SUBPATH', '/'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)) )