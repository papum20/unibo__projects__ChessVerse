from enum import IntEnum


# Enums
class EventType(IntEnum):
    ERROR = -1
    RESIGN = 0
    MOVE = 1
    POP = 2
    ACK = 3
    CONFIG = 4
    END = 5
    START = 999


class GameType(IntEnum):
    PVP = 0
    PVE = 1
    DAILY = 2
    WEEKLY = 3
    RANKED = 4


class AckType(IntEnum):
    OK = 0
    NOK = 1
    UNKNOWN_ACTION = 2
    WRONG_CONFIG = 3
    NOT_IMPLEMENTED = 4
    GAME_NOT_FOUND = 5
    WRONG_TURN = 6


# pveGame constants
MIN_RANK = 0
MAX_RANK = 100

MIN_DEPTH = 1
MAX_DEPTH = 20

MIN_TIME = 1
MAX_TIME = 3000

# pvpGame constants
TIME_OPTIONS = [300, 600, 900]

DEFAULT_ELO = 1000

# game modes

## ranked
MODE_RANKED_K = 1  # see GameRanked formula

### pts changed in rakned. It's a tuple of (win, draw, lose)
MODE_RANKED_PT_DIFF = (8, 0, -2)

FIELDS = ("EloReallyBadChess", "score_ranked")
