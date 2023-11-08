import eel
from screeninfo import get_monitors
import requests
from websockets.sync.client import connect
import json
import chess
from enum import IntEnum


def get_full_screen_size():
    monitors = get_monitors()
    screen_width = max(m.width for m in monitors)
    screen_height = max(m.height for m in monitors)
    return screen_width, screen_height


screen_width, screen_height = get_full_screen_size()

eel.init('web')


@eel.expose
def frontend_add_guest():
    response = requests.get('http://localhost:8080/backend_django/add_guest/')
    return response.json()


@eel.expose
def frontend_get_guest_name():
    response = requests.get('http://localhost:8080/backend_django/get_guest_name/')
    data = response.json()
    return data['guest_nickname']


eel.start('login/login.html', size=(screen_width, screen_height))


class EventType(IntEnum):
    ERROR = -1
    RESIGN = 0
    MOVE = 1
    POP = 2
    ACK = 3
    CONFIG = 4
    END = 5
    START = 999


class AckType(IntEnum):
    OK = 0
    NOK = 1
    UNKNOWN_ACTION = 2
    WRONG_CONFIG = 3
    NOT_IMPLEMENTED = 4
    GAME_NOT_FOUND = 5
    WRONG_TURN = 6


class Player:
    last_move = None

    def __init__(self, websocket, game_type, color=None, board=None, remaining_time=None):
        self.game_id = None
        self.game_type = game_type
        self.ws = websocket
        self.color = color
        self.board = board
        self.remaining_time = remaining_time

    def config(self, fen, color, remaining_time=-1):
        self.board = chess.Board(fen)
        self.color = color == "0"
        self.remaining_time = remaining_time
        # TODO non ha senso passare remaining_time al server e poi farselo rimandare in dietro. salvarlo direttamente

    def validate_move(self, uci):
        try:
            move = chess.Move.from_uci(uci)
            if move in self.board.legal_moves:
                return move
            else:
                return None  # Return None for invalid moves
        except ValueError:
            return None

    def print_board(self):
        print(self.board)

    def resign(self):
        return {"event": 0, "data": {"id": self.game_id, "type": self.gameType}}

    def move(self):
        uci = input("Enter UCI move:")
        validated_move = self.validate_move(uci)
        if validated_move is not None:
            return {
                "event": EventType.MOVE.value,
                "data": {"value": uci, "id": self.game_id, "type": self.gameType},
            }
        else:
            print("Invalid move. Try again.")
            return None

    def pop(self):
        return {"event": EventType.POP.value, "data": {"id": self.game_id, "type": self.gameType}}

    def select(self):
        try:
            square = input(
                "Enter the square (e.g., 'e2') of the piece you want to move: "
            )
            selected_square = chess.parse_square(square)
            piece_moves = list(
                filter(
                    lambda move: move.from_square == selected_square,
                    self.board.legal_moves,
                )
            )
            print(
                f"Legal moves for {square}: {', '.join(str(move) for move in piece_moves)}"
            )
        except (ValueError, KeyError):
            print("Invalid square. Try again.")

    def play(self):
        actions = {"s": self.select, "m": self.move, "r": self.resign, "p": self.pop}
        while True:
            opt = input("inserisci un opzione: nella forma (s, p, r, m) ")
            action_method = actions.get(opt)
            if action_method is not None:
                to_send = action_method()
                if to_send is not None:
                    break
            else:
                print("Opzione non valida. Riprova.")
        self.ws.send(json.dumps(to_send))
        self.last_move = to_send

    def handler(self, message):
        handlers = {
            EventType.MOVE.value: self.handle_move,
            EventType.POP.value: self.handle_pop,
            EventType.ACK.value: self.handle_ack,
            EventType.CONFIG.value: self.handle_config,
            EventType.END.value: self.handle_end,
            EventType.ERROR.value: self.handle_fatal_error,
        }
        handler = handlers.get((message["event"]))
        if handler:
            handler(message)
        else:
            print(f"Errore: {message} {handlers}")

    @staticmethod
    def handle_fatal_error(_):
        exit(1)

    def handle_config(self, message):
        self.config(message["data"]["fen"], message["data"]["color"])
        print("color:", message["data"]["color"])
        print(self.board)
        print(f"Playing as {'white' if message['data']['color'] == 0 else 'black'}")
        self.game_id = message["data"]["id"]
        if message["data"]["color"] == 0:
            self.play()

    def handle_ack(self, message):
        if "time" in message["data"].keys():
            self.remaining_time = message["data"]["time"]
        if message["data"]["value"] not in [0, EventType.POP]:
            print("operazione rifiutata, riprova con altra mossa")
            self.play()
        elif self.last_move["event"] == EventType.MOVE.value:
            self.board.push(chess.Move.from_uci(self.last_move["data"]["value"]))
            self.print_board()
        elif self.last_move["event"] == EventType.POP.value:
            self.board.pop()
            self.board.pop()
            self.print_board()
            self.play()
        else:
            self.ws.close()

    @staticmethod
    def handle_end(message):
        # print(f"hai {"vinto" if message["data"]["value"] else "perso"}")
        pass

    @eel.expose
    def handle_move(self, message):
        self.board.push(chess.Move.from_uci(message["data"]["value"]))
        print(self.board)
        self.play()

    def handle_pop(self):
        self.board.pop()
        self.board.pop()
        print(self.board)
        # self.play()


# se ricevo l'ack non agisco, ma resto in ascolto,
# finche' non ricevo una delle azioni, se ricevo una
# delle azioni posso scegliere la mia mossa

"""
  1) connetti al server
  2) carica configurazione inviata dal server
  3) se mio turno, fai una mossa, manda al server, aspetta per ack
  4) se non mio turno, aspetta messaggio dal server
"""


@eel.expose
def game(depth, rank, game_type="PVE", time=10):
    infos = dict(
        event=EventType.START,
        data=dict(
            type=1 if game_type == "PVE" else 0,
            depth=max(min(depth, 20), 1),
            rank=max(min(rank, 100), 0),
            time=time,
        ),
    )
    with connect("ws://localhost:8766") as websocket:
        player = Player(websocket, 1 if game_type == "PVE" else 0)
        player.ws.send(json.dumps(infos))
        print("successo")
        while True:
            message = json.loads(player.ws.recv())
            print(message)
            player.handler(message)
            if message["event"] == 5:
                break
        player.ws.close()


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "-m",
#         choices=["PVE", "PVP"],
#         required=True,
#         help="Play against Stockfish v16 (PvE) or against another player (PvP)",
#     )
#     parser.add_argument("-l", type=int, default=5, help="Bot strength level [1,20]")
#     parser.add_argument("-r", type=int, default=50, help="Game rank [0, 100]")
#     parser.add_argument("-t", type=int, default=5, help="Game time [5, 10, 15, -1]")
#     args = parser.parse_args()
#
#     gameType = 1 if args.m == "PVE" else 0
#
#     infos = dict(
#         event=EventType.START,
#         data=dict(
#             type=1 if args.m == "PVE" else 0,
#             depth=max(min(args.l, 20), 1),
#             rank=max(min(args.r, 100), 0),
#             time=args.t,
#         ),
#     )
