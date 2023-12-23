from time import perf_counter


class Player:
    def __init__(self, sid: str, color: bool, time: int):
        self.sid = sid
        self.color = color
        self.time = time
        self.is_timed = time != -1
        if self.is_timed:
            self.remaining_time = time
            self.latest_timestamp = perf_counter()
        self.move_count = 0

    def __eq__(self, sid: str):
        return self.sid == sid

    def add_time(self, time: int):
        if self.is_timed:
            self.remaining_time += time

    def update_time(self):
        if self.is_timed:
            self.remaining_time -= perf_counter() - self.latest_timestamp
            self.latest_timestamp = perf_counter()

    def has_time(self, update=True):
        if update:
            self.update_time()
        return not self.is_timed or self.remaining_time > 0
