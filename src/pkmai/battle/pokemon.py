from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, List, Literal, Tuple

from pkmai.battle.db import PokemonDB
from pkmai.battle.move import Move
from pkmai.battle.moveset import Moveset
from pkmai.battle.stats import Stats


class PokemonParser:
    @classmethod
    def parse_ident(cls, ident: str) -> Tuple[str, str]:
        player_id, name = ident.split(": ", maxsplit=1)
        return player_id, name

    @classmethod
    def parse_active_ident(cls, ident: str) -> Tuple[str, str, str]:
        res, name = cls.parse_ident(ident)
        return res[:-1], res[-1], name

    @classmethod
    def parse_detail(cls, detail: str) -> Tuple[str, Literal["M", "F", ""], int]:
        details = detail.split(", ")
        species = details[0]
        gender: Literal["M", "F", ""] = ""
        level = 100
        for detail in details[1:]:
            if detail == "M":
                gender = "M"
            elif detail == "F":
                gender = "F"
            elif detail.startswith("L"):
                level = int(detail[1:])
        return species, gender, level

    @classmethod
    def parse_condition(cls, condition: str) -> Tuple[int, int, str]:
        conditions = condition.split(" ")
        hps = conditions[0].split("/")
        if len(hps) == 2:
            hp, total_hp = int(hps[0]), int(hps[1])
        else:
            hp, total_hp = 0, 0
        if len(conditions) == 2:
            status = conditions[1]
        else:
            status = ""
        return hp, total_hp, status


@dataclass
class Pokemon:
    name_or_id: InitVar[str]
    id: str = ""
    name: str = ""
    nickname: str = ""
    level: int = 100
    gender: Literal["M", "F", ""] = ""
    types: List[str] = field(default_factory=list)
    current_hp: int = 100
    total_hp: int = 100
    status: str = ""
    stats: Stats = field(default_factory=Stats)
    moveset: Moveset = field(default_factory=Moveset)
    ability: str = ""
    base_ability: str = ""
    item: str = ""
    can_mega: bool = False

    need_additional: InitVar[bool] = True
    pokemon_db: InitVar[Dict[str, Any]] = None

    def __post_init__(
        self,
        name_or_id: str,
        need_additional: bool = True,
        pokemon_db: Dict[str, Any] = None,
    ):
        if need_additional:
            self.load_additional(name_or_id, pokemon_db)

    def load_additional(
        self,
        name_or_id: str,
        pokemon_db: Dict[str, Any] = None,
    ):
        pokemon_db = pokemon_db or PokemonDB.item(name_or_id)

        self.id = self.id or PokemonDB.to_id(name_or_id)
        self.name = self.name or pokemon_db["name"]
        self.types = self.types or pokemon_db["types"]

    # ---------------------------------- Request --------------------------------- #

    @classmethod
    def init_from_pokemon_request(cls, pokemon_request: Dict[str, Any]) -> Pokemon:
        _, nickname = PokemonParser.parse_ident(pokemon_request["ident"])
        name, gender, level = PokemonParser.parse_detail(pokemon_request["details"])
        current_hp, total_hp, status = PokemonParser.parse_condition(
            pokemon_request["condition"]
        )

        stats = Stats.init_from_stats_request(pokemon_request["stats"])
        moveset = Moveset.init_normal_move_from_move_list_request(
            pokemon_request["moves"]
        )

        ability = pokemon_request["ability"]
        base_ability = pokemon_request["baseAbility"]
        item = pokemon_request["item"]

        return cls(
            name,
            "",
            name,
            nickname,
            level,
            gender,
            [],
            current_hp,
            total_hp,
            status,
            stats,
            moveset,
            ability,
            base_ability,
            item,
        )

    def update_attr_from_active_request(self, active_request: Dict[str, Any]):
        self.can_mega == "canMegaEvo" in active_request
        self.moveset.init_all_move_types_from_active_request(active_request)

    # ---------------------------------- Choose ---------------------------------- #

    def list_all_possible_choices(self) -> Dict[str, Move]:
        return self.moveset.list_all_possible_choices(self.can_mega)
