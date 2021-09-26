import json
from typing import Dict, List

from pkmai.room.chat import Chat
from pkmai.room.room import compute_all_listeners
from pkmai.utils.type import GlobalData, PlayerData, PokemonData, RequestData
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
        self.rules: Dict[str, str] = {}
        self.listeners.update(compute_all_listeners(self))
        self.request: RequestData = {}

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
            if raw.get("forceSwitch"):
                self.request["force_switch"] = True
            elif raw.get("active"):
                raw_active = raw["active"][0]
                self.request["active"] = {
                    "moves": raw_active["moves"],
                    "can_dynamax": raw_active.get("canDynamax", False),
                }
                if self.request["active"]["can_dynamax"]:
                    self.request["active"]["max_moves"] = raw_active["maxMoves"][
                        "maxMoves"
                    ]
            if raw.get("noCancel"):
                self.request["no_cancel"] = True
            raw_side = raw["side"]
            self.request["side"] = {
                "name": raw_side["name"],
                "id": raw_side["id"],
                "pokemons": [],
            }
            for pokemon_data in raw_side["pokemon"]:
                details = pokemon_data["details"].split(", ")
                pokemon: PokemonData = {
                    "ident": pokemon_data["ident"],
                    "species": details[0],
                    "level": 100,
                }
                for detail in details[1:]:
                    if detail == "M" or detail == "F":
                        pokemon["gender"] = detail
                    elif detail.startswith("L"):
                        pokemon["level"] = int(detail[1:])
                current_hp, total_hp = pokemon_data["condition"].split("/")
                pokemon["current_hp"] = int(current_hp)
                pokemon["total_hp"] = int(total_hp)
                pokemon["active"] = pokemon_data["active"]
                pokemon["moves"] = pokemon_data["moves"]
                pokemon["base_ability"] = pokemon_data["baseAbility"]
                pokemon["item"] = pokemon_data["item"]
                pokemon["pokeball"] = pokemon_data["pokeball"]
                pokemon["ability"] = pokemon_data["ability"]
                self.request["side"]["pokemons"].append(pokemon)
            self.request["rqid"] = raw["rqid"]
