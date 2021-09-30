import json
from typing import Dict, List, Literal, Tuple, Union

from pkmai.choose.choose import (
    Choose,
    SinglePokemonChoose,
    SwitchChoose,
    parse_pokemon_choose,
    parse_switch_choose,
)
from pkmai.room.chat import Chat
from pkmai.room.room import compute_all_listeners
from pkmai.utils.type import (
    ActiveData,
    GlobalData,
    PlayerData,
    PokemonData,
    RequestData,
    SideData,
)
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
        self.requests: List[RequestData] = []

    # -------------------------------- User Method ------------------------------- #

    async def forfeit(self, leave: bool = True):
        await self.send("/forfeit")
        if leave:
            await self.leave()

    async def choose(self, choice: Union[str, Choose]):
        await self.send(f"/choose {choice}")

    async def choose_default(self):
        await self.choose("default")

    async def choose_undo(self):
        await self.choose("undo")

    def get_all_valid_pokemon_chooses(self) -> List[SinglePokemonChoose]:
        return parse_pokemon_choose(self.requests[-1]["active"])

    def get_all_valid_switch_chooses(self) -> List[SwitchChoose]:
        return parse_switch_choose(self.requests[-1]["side"]["pokemons"])

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
            request: RequestData = {}
            if "forceSwitch" in raw:
                request["force_switch"] = True
            if "noCancel" in raw:
                request["no_cancel"] = True
            if "active" in raw:
                request["active"] = self.parse_request_active(raw["active"][0])
            request["side"] = self.parse_request_side(raw["side"])
            request["rqid"] = raw["rqid"]
            self.requests.append(request)

    # ----------------------------------- Util ----------------------------------- #

    @staticmethod
    def parse_pokemon_condition(condition: str) -> Tuple[int, int, str]:
        conditions = condition.split(" ")
        hps = conditions[0].split("/")
        if len(hps) == 2:
            current_hp, total_hp = int(hps[0]), int(hps[1])
        else:
            current_hp, total_hp = 0, 0
        if len(conditions) == 2:
            status = conditions[1]
        else:
            status = ""
        return current_hp, total_hp, status

    @staticmethod
    def parse_pokemon_detail(detail: str) -> Tuple[str, Literal["M", "F", "N"], int]:
        details = detail.split(", ")
        species = details[0]
        gender: Literal["M", "F", "N"] = "N"
        level = 100
        for detail in details[1:]:
            if detail == "M":
                gender = "M"
            elif detail == "F":
                gender = "F"
            elif detail.startswith("L"):
                level = int(detail[1:])
        return species, gender, level

    @staticmethod
    def parse_request_pokemon(pokemon_raw: Dict) -> PokemonData:
        pokemon: PokemonData = {"ident": pokemon_raw["ident"]}
        species, gender, level = Battle.parse_pokemon_detail(pokemon_raw["details"])
        pokemon.update({"species": species, "gender": gender, "level": level})

        current_hp, total_hp, status = Battle.parse_pokemon_condition(
            pokemon_raw["condition"]
        )
        pokemon.update(
            {"current_hp": current_hp, "total_hp": total_hp, "status": status}
        )

        pokemon["active"] = pokemon_raw["active"]
        pokemon["moves"] = pokemon_raw["moves"]
        pokemon["base_ability"] = pokemon_raw["baseAbility"]
        pokemon["item"] = pokemon_raw["item"]
        pokemon["pokeball"] = pokemon_raw["pokeball"]
        pokemon["ability"] = pokemon_raw["ability"]

        return pokemon

    @staticmethod
    def parse_request_active(active_raw: Dict) -> ActiveData:
        active: ActiveData = {
            "moves": active_raw["moves"],
        }
        if "canDynamax" in active_raw:
            active["can_dynamax"] = True
        if "maxMoves" in active_raw:
            active["max_moves"] = active_raw["maxMoves"]["maxMoves"]
        if "canMegaEvo" in active_raw:
            active["can_mega_evo"] = True
        if "canZMove" in active_raw:
            active["can_z_move"] = active_raw["canZMove"]
        return active

    @staticmethod
    def parse_request_side(side_raw: Dict) -> SideData:
        side: SideData = {
            "name": side_raw["name"],
            "id": side_raw["id"],
            "pokemons": [],
        }
        for pokemon_raw in side_raw["pokemon"]:
            side["pokemons"].append(Battle.parse_request_pokemon(pokemon_raw))
        return side
