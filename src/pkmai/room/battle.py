from typing import Dict, List

from pkmai.room.chat import Chat
from pkmai.utils.type import GlobalData, PlayerData
from websockets.legacy.client import WebSocketClientProtocol


class Battle(Chat):
    def __init__(
        self,
        conn: WebSocketClientProtocol,
        data: GlobalData,
        room_id: str,
        debug: bool = False,
        logs: List[List[str]] = None,
    ) -> None:
        super().__init__(
            conn, data, room_id, debug=debug, logs=logs, good_after_msg_type="start"
        )
        self.players: Dict[str, PlayerData] = {}
        self.rules: Dict[str, str] = {}
        self.listeners.update(
            {
                "player": self.__player,
                "teamsize": self.__teamsize,
                "gametype": self.__gametype,
                "gen": self.__gen,
                "tier": self.__tier,
                "rule": self.__rule,
            }
        )

    # -------------------------------- User Method ------------------------------- #

    async def forfeit(self, leave: bool = True):
        await self.send("/forfeit")
        if leave:
            await self.leave()

    # --------------------------------- Listener --------------------------------- #

    def __player(self, msg: List[str]):
        self.players[msg[0]] = {"name": msg[1]}
        if msg[2]:
            self.players[msg[0]]["rating"] = int(msg[2])
        if msg[1] == self.data["username"]:
            self.self_id = msg[0]

    def __teamsize(self, msg: List[str]):
        self.players[msg[0]]["teamsize"] = int(msg[1])

    def __gametype(self, msg: List[str]):
        self.gametype = msg[0]

    def __gen(self, msg: List[str]):
        self.gen = int(msg[0])

    def __tier(self, msg: List[str]):
        self.tier = msg[0]

    def __rule(self, msg: List[str]):
        name, des = msg[0].split(": ")
        self.rules[name] = des
