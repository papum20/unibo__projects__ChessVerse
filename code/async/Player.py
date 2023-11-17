from time import perf_counter

class Player:
    def __init__(self, sid, color, time):
        self.id = sid
        self.color = color
        self.isTimed = time != -1
        if self.isTimed:
            self.remainingTime = time * 60
            self.latestTimeStamp = perf_counter()

    def update_time(self):
        if self.isTimed:
            self.remainingTime -= perf_counter() - self.latestTimeStamp
            self.latestTimeStamp = perf_counter()

    def has_time(self):
        return not self.isTimed or self.remainingTime > 0

    def get_config_msg(self):
        return {"fen": self.fen, "color": self.color}

    def get_end_msg(self, winner: int):
        return {"value": int(self.color == winner)}

    async def get_move_msg(self, move: str, success: bool = True):
        return {"value": move, "success": success}