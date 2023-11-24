import json
from time import perf_counter


class Player:
    def __init__(self, sid, color, time):
        self.id = sid
        self.color = color
        time = int(time)
        self.is_timed = time != -1
        if self.is_timed:
            self.remaining_time = time
            self.latest_timestamp = perf_counter()
        self.first_move = True

    def add_time(self, time):
        if self.is_timed:
            self.remaining_time += time

    def update_time(self):
        if self.is_timed:
            if not self.first_move:
                self.remaining_time -= perf_counter() - self.latest_timestamp
            self.latest_timestamp = perf_counter()

    def has_time(self, update=True):
        if update:
            self.update_time()
        return not self.is_timed or self.remaining_time > 0

    def get_config_msg(self):
        return json.dumps({"fen": self.fen, "color": self.color})

    def get_end_msg(self, winner: int):
        return json.dumps({"value": int(self.color == winner)})

    async def get_move_msg(self, move: str, success: bool = True):
        return json.dumps({"value": move, "success": success})
