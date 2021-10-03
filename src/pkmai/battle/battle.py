import json
from typing import Dict, List

from pkmai.battle.team import Team
from pkmai.room.chat import Chat
from pkmai.room.room import compute_all_listeners
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
            conn, data, room_id, debug=debug, logs=logs, custom_good_event=True
        )
        self.players: Dict[str, PlayerData] = {}
        self.teams: Dict[str, Team] = {}
        self.rules: Dict[str, str] = {}
        self.listeners.update(compute_all_listeners(self))

    # -------------------------------- User Method ------------------------------- #

    async def forfeit(self, leave: bool = True):
        await self.send("/forfeit")
        if leave:
            await self.leave()

    async def choose(self, choice: str):
        await self.send(f"/choose {choice}")

    async def choose_default(self):
        await self.choose("default")

    async def choose_undo(self):
        await self.choose("undo")

    # --------------------------------- Listener --------------------------------- #

    def listener_player(self, msg: List[str]):
        self.players[msg[0]] = {"name": msg[1]}
        if msg[3]:
            self.players[msg[0]]["rating"] = int(msg[3])
        if msg[1] == self.data["username"]:
            self.self_id = msg[0]

    def listener_teamsize(self, msg: List[str]):
        self.players[msg[0]]["teamsize"] = int(msg[1])

    def listener_gametype(self, msg: List[str]):
        self.gametype = msg[0]

    def listener_gen(self, msg: List[str]):
        self.gen = int(msg[0])

    def listener_tier(self, msg: List[str]):
        self.tier = msg[0]

    def listener_rule(self, msg: List[str]):
        name, des = msg[0].split(": ")
        self.rules[name] = des

    def listener_turn(self, msg: List[str]):
        turn = int(msg[0])
        if turn == 1:
            self.is_good.set()

    def listener_request(self, msg: List[str]):
        if msg[0]:
            raw = json.loads(msg[0])
            team = Team()
            team.pokemon_from_request(raw)
            self.teams[self.self_id] = team
