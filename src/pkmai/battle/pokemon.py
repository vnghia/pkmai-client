from __future__ import annotations

from typing import Dict, Literal, Tuple

from pkmai.battle.move import MoveSet
from pkmai.battle.stats import Stats


class Pokemon:
    def __init__(
        self,
        player_id: str,
        name: str,
        species: str,
        level: int,
        gender: Literal["M", "F", ""],
        total_hp: int,
        stats: Stats = None,
        moveset: MoveSet = None,
        base_ability: str = "",
        item: str = "",
    ) -> None:
        self._player_id = player_id
        self._name = name
        self._species = species
        self._level = level
        self._gender = gender
        self._hp = total_hp
        self._total_hp = total_hp
        self._stats = stats or Stats()
        self._status = ""
        self._moveset = moveset or MoveSet()
        self._ability = base_ability
        self._base_ability = base_ability
        self._item = item
        self._state: Literal["", "mega", "max"] = ""
        self._can_mega = False

    @property
    def player_id(self) -> str:
        return self._player_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def species(self) -> str:
        return self._species

    @property
    def level(self) -> int:
        return self._level

    @property
    def gender(self) -> Literal["M", "F", ""]:
        return self._gender

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, hp: int):
        self._hp = hp

    @property
    def total_hp(self) -> int:
        return self._total_hp

    @property
    def stats(self) -> Stats:
        return self._stats

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str):
        self._status = status

    @property
    def moveset(self) -> MoveSet:
        return self._moveset

    @property
    def ability(self) -> str:
        return self._ability

    @ability.setter
    def ability(self, ability: str):
        self._ability = ability

    @property
    def base_ability(self) -> str:
        return self._base_ability

    @property
    def item(self) -> str:
        return self._item

    @item.setter
    def item(self, item: str):
        self._item = item

    @property
    def state(self) -> Literal["", "mega", "max"]:
        return self._state

    @state.setter
    def state(self, state: Literal["", "mega", "max"]):
        self._state = state
        self._moveset.max = state == "max"

    @property
    def can_mega(self) -> bool:
        return self._can_mega

    # ---------------------------------- String ---------------------------------- #

    def __repr__(self) -> str:
        return f"({hex(id(self))}) {self}"

    def __str__(self) -> str:
        return f"{self.name}, {self.species}, {self.level}\n{self.moveset}"

    # ----------------------------------- Copy ----------------------------------- #

    def clone(self) -> Pokemon:
        clone = Pokemon(
            self._player_id,
            self._name,
            self._species,
            self._level,
            self._gender,
            self._total_hp,
            self._stats.clone(),
            self._moveset.clone(),
            self._base_ability,
            self._item,
        )
        clone._status = self._status
        clone._ability = self._ability
        clone._state = self._state
        clone._can_mega = self._can_mega
        return clone

    # ---------------------------------- Parsing --------------------------------- #

    @staticmethod
    def parse_ident(ident: str) -> Tuple[str, str]:
        player_id, name = ident.split(": ", maxsplit=1)
        return player_id, name

    @staticmethod
    def parse_active_ident(ident: str) -> Tuple[str, str, str]:
        res, name = Pokemon.parse_ident(ident)
        return res[:-1], res[-1], name

    @staticmethod
    def parse_detail(detail: str) -> Tuple[str, Literal["M", "F", ""], int]:
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

    @staticmethod
    def parse_condition(condition: str) -> Tuple[int, int, str]:
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

    # ---------------------------------- Request --------------------------------- #

    @classmethod
    def create_from_request(cls, pokemon_dict: Dict) -> Pokemon:
        ident = pokemon_dict["ident"]
        player_id, name = cls.parse_ident(ident)
        species, gender, level = cls.parse_detail(pokemon_dict["details"])
        _, total_hp, _ = cls.parse_condition(pokemon_dict["condition"])

        stat_table = Stats.create_from_request(pokemon_dict["stats"])
        base_ability = pokemon_dict["baseAbility"]
        item = pokemon_dict["item"]

        moveset = MoveSet()
        for move in pokemon_dict["moves"]:
            moveset.add_used_move(move, used=False)

        return cls(
            player_id,
            name,
            species,
            level,
            gender,
            total_hp,
            stat_table,
            moveset,
            base_ability,
            item,
        )
