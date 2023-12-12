from enum import IntEnum, StrEnum


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
	RANKED = 2

class AckType(IntEnum):
	OK = 0
	NOK = 1
	UNKNOWN_ACTION = 2
	WRONG_CONFIG = 3
	NOT_IMPLEMENTED = 4
	GAME_NOT_FOUND = 5
	WRONG_TURN = 6

# fields	
## users
RANKS = (
	"EloReallyBadChess",
	"ranked"	
)

# pveGame constants
MIN_RANK = 0
MAX_RANK = 100

MIN_DEPTH = 1
MAX_DEPTH = 20

MIN_TIME = 1
MAX_TIME = 3000

# pvpGame constants
TIME_OPTIONS = [300, 600, 900]
