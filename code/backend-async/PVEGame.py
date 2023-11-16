import Game

class PVEGame(Game):
    def __init__(self, player, rank, depth, time):
        super().__init__([player], rank, time)
        self.bot = None
        self.depth = depth

    async def initialize_bot(self):
        self.bot = (await chess.engine.popen_uci("./stockfish"))[1]

    async def end_game(self, winner: bool):
        await self.current().send_end(winner)

    async def recv_event(self, msg):
        if msg["event"] == EventType.RESIGN:
            await self.end_game(False)
            pass
        elif msg["event"] == EventType.MOVE:
            if not self.current().has_time():
                await self.end_game(False)
            else:
                while (
                        chess.Move.from_san(msg["data"]["value"])
                        not in self.board.legal_moves
                ):
                    await self.current().send_ack(AckType.NOK, True)
                self.board.push_san(msg["data"]["value"])
                self.popped = False
                if self.board.outcome() is None:
                    await self.current().send_ack(AckType.OK, True)
                    bot_move = (
                        await self.bot.play(
                            self.board, chess.engine.Limit(depth=self.depth)
                        )
                    ).move.san()
                    self.board.push_san(bot_move)
                    if self.board.outcome() is None:
                        await self.current().send_move(bot_move)
                    else:
                        await self.current().send_end(False)
                else:
                    await self.end_game(True)
        elif msg["event"] == EventType.POP:
            if not self.current().has_time():
                await self.current().send_end(False)
            elif self.popped:
                await self.current().send_ack(AckType.OK, True)
            else:
                try:
                    m1 = self.board.pop()
                    try:
                        self.board.pop()
                    except IndexError:
                        self.board.push(m1)
                        raise IndexError
                except IndexError:
                    await self.current().send_ack(AckType.NOK, True)
                else:
                    await self.current().send_ack(AckType.OK, True)
        else:
            await self.current().send_ack(AckType.UNKNOWN_ACTION)