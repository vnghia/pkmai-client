from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

from pkmai.battle.move import Move
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
        moves: List[Move] = None,
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
        self._moves = moves or []
        self._max_moves: List[Move] = []
        self._zmoves: List[Optional[Move]] = []
        self._ability = base_ability
        self._base_ability = base_ability
        self._item = item
        self._state: Literal["", "mega", "max"] = ""
        self._can_mega = False
        self._can_max = False
        self._can_zmove = False

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
    def moves(self) -> List[Move]:
        if self._state == "max":
            return self._max_moves
        else:
            return self._moves

    @property
    def zmoves(self) -> List[Optional[Move]]:
        if self._can_zmove:
            raise ValueError("Can not zmove")
        return self._zmoves

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
        if (not self._can_mega and state == "mega") or (
            not self._can_max and state == "max"
        ):
            raise ValueError(f"Can not {state}")
        elif state == "" and self._state == "max":
            self._max_moves.clear()
        self._state = state

    @property
    def can_mega(self) -> bool:
        return self._can_mega

    @property
    def can_max(self) -> bool:
        return self._can_max

    @property
    def can_zmove(self) -> bool:
        return self._can_zmove

    @can_zmove.setter
    def can_zmove(self, can_zmove: bool):
        if self._can_zmove and not can_zmove:
            self._zmoves.clear()
            self._can_zmove = can_zmove

    # ---------------------------------- String ---------------------------------- #

    def __repr__(self) -> str:
        return f"({hex(id(self))}) {self}"

    def __str__(self) -> str:
        return f"{self.name}, {self.species}, {self.level}\n{'; '.join(map(str, self.moves))}"

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
            [move.clone() for move in self._moves],
            self._base_ability,
            self._item,
        )
        clone._status = self._status
        clone._max_moves = self._max_moves
        clone._zmoves = self._zmoves
        clone._ability = self._ability
        clone._state = self._state
        clone._can_mega = self._can_mega
        clone._can_max = self._can_max
        clone._can_zmove = self._can_zmove
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

        moves: List[Move] = []
        for move in pokemon_dict["moves"]:
            moves.append(Move(move))

        return cls(
            player_id,
            name,
            species,
            level,
            gender,
            total_hp,
            stat_table,
            moves,
            base_ability,
            item,
        )

    def __update_moves_from_request(self, move_list: List[Dict]):
        for move, move_dict in zip(self.moves, move_list):
            move.update_from_request(move_dict)

    def __update_max_moves_from_request(self, max_move_list: List[Dict]):
        if not self._max_moves:
            for move, max_move_dict in zip(self.moves, max_move_list):
                max_move = Move(
                    max_move_dict["move"],
                    maxpp=move.maxpp,
                    target=max_move_dict["target"],
                    type="max",
                )
                max_move.pp = move.pp
                self._max_moves.append(max_move)
        else:
            for move, max_move in zip(self.moves, self._max_moves):
                max_move.pp = move.pp

    def __update_zmoves_from_request(self, z_move_list: List[Dict]):
        for z_move_dict in z_move_list:
            if not z_move_list:
                self._zmoves.append(None)
            else:
                self._zmoves.append(
                    Move(
                        z_move_dict["move"],
                        maxpp=1,
                        target=z_move_dict["target"],
                        type="zmove",
                    )
                )

    def update_active_from_request(self, active_dict: Dict):
        self.__update_moves_from_request(active_dict["moves"])
        self._can_max = "canDynamax" in active_dict
        self._can_mega = "canMegaEvo" in active_dict
        self._can_zmove = "canZMove" in active_dict
        if self._can_zmove:
            self.__update_zmoves_from_request(active_dict["canZMove"])
        if "maxMoves" in active_dict:
            self.__update_max_moves_from_request(active_dict["maxMoves"]["maxMoves"])
        elif "maxMoves" not in active_dict and self._max_moves:
            self.state = ""

    def update_from_request(self, pokemon_dict: Dict):
        hp, _, status = self.parse_condition(pokemon_dict["condition"])
        self.hp = hp
        self.status = status
        self.stats.update_from_request(pokemon_dict["stats"])
        self.ability = pokemon_dict["ability"]
        self.item = pokemon_dict["item"]
