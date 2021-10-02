from __future__ import annotations

from typing import Dict, List, Literal

from pkmai.battle.db import MoveDB


class Move:
    def __init__(
        self,
        id: str,
        name: str = "",
        maxpp: int = 0,
        target: Literal[
            "adjacentAlly",
            "adjacentAllyOrSelf",
            "adjacentFoe",
            "all",
            "allAdjacent",
            "allAdjacentFoes",
            "allies",
            "allySide",
            "allyTeam",
            "any",
            "foeSide",
            "normal",
            "randomNormal",
            "scripted",
            "self",
        ] = "normal",
        type: Literal["", "zmove", "max"] = "",
    ) -> None:
        self._name = name
        self._id = id
        self._pp = maxpp
        self._maxpp = maxpp
        self._target = target
        self._type = type
        if self._type == "zmove":
            self._maxpp = 1
        self._disable = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> str:
        return self._id

    @property
    def pp(self) -> int:
        return self._pp

    @pp.setter
    def pp(self, pp: int):
        self._pp = pp

    @property
    def maxpp(self) -> int:
        return self._maxpp

    @property
    def target(
        self,
    ) -> Literal[
        "adjacentAlly",
        "adjacentAllyOrSelf",
        "adjacentFoe",
        "all",
        "allAdjacent",
        "allAdjacentFoes",
        "allies",
        "allySide",
        "allyTeam",
        "any",
        "foeSide",
        "normal",
        "randomNormal",
        "scripted",
        "self",
    ]:
        return self._target

    @property
    def type(self) -> Literal["", "zmove", "max"]:
        return self._type

    @property
    def disable(self) -> bool:
        return self._disable

    # ---------------------------------- String ---------------------------------- #

    def __repr__(self) -> str:
        return f"({hex(id(self))}) {self}"

    def __str__(self) -> str:
        return self.name if self.name else self.id

    # ----------------------------------- Copy ----------------------------------- #

    def clone(self) -> Move:
        clone = Move(self.id, self.name, self.maxpp, self.target, self.type)
        clone._pp = self._pp
        clone._disable = self._disable
        return clone

    # ---------------------------------- Request --------------------------------- #

    def update_from_request(self, move_dict: Dict):
        if not self._name:
            self._name = move_dict["move"]
        if not self._maxpp:
            self._maxpp = int(move_dict["maxpp"])
        if not self.target:
            self._target = move_dict["target"]
        self._pp = int(move_dict["pp"])
        self._disable = "disable" in move_dict


class MoveSet:
    def __init__(
        self,
        moves: List[Move] = None,
        max_moves: List[Move] = None,
        max_moves_to_moves: Dict[str, str] = None,
        zmoves: List[Move] = None,
        can_max: bool = False,
        can_z: bool = False,
        max: bool = False,
    ):
        self._moves = moves or []
        self._max_moves = max_moves or []
        self._max_moves_to_moves = max_moves_to_moves or {}
        self._moves_to_max_moves = {
            value: key for key, value in self._max_moves_to_moves.items()
        }
        self._zmoves = zmoves or []
        self._moves_name: Dict[str, int] = {
            move.name: idx for idx, move in enumerate(self._moves)
        }
        self._max_moves_name: Dict[str, int] = {
            move.name: idx for idx, move in enumerate(self._max_moves)
        }
        self._zmoves_name: Dict[str, int] = {
            move.name: idx for idx, move in enumerate(self._zmoves)
        }
        self._can_max = can_max
        self._can_z = can_z
        self._max = max

    @property
    def current(self) -> List[Move]:
        current_set = self.moves if not self.max else self.max_moves
        return current_set + self.zmoves

    @property
    def moves(self) -> List[Move]:
        return self._moves

    @property
    def max_moves(self) -> List[Move]:
        if not self.can_max:
            return []
        return self._max_moves

    def __set_max_moves_to_moves(self, max_moves_to_moves: Dict[str, str]):
        self._max_moves_to_moves = max_moves_to_moves
        self._moves_to_max_moves = {
            value: key for key, value in self._max_moves_to_moves.items()
        }

    max_moves_to_moves = property(fset=__set_max_moves_to_moves)
    del __set_max_moves_to_moves

    @property
    def zmoves(self) -> List[Move]:
        if not self.can_z:
            return []
        return self._zmoves

    @property
    def moves_name(self) -> Dict[str, int]:
        return self._moves_name

    @property
    def max_moves_name(self) -> Dict[str, int]:
        if not self.can_max:
            return {}
        return self._max_moves_name

    @property
    def zmoves_name(self) -> Dict[str, int]:
        if not self.can_z:
            return {}
        return self._zmoves_name

    @property
    def can_max(self) -> bool:
        return self._can_max

    @can_max.setter
    def can_max(self, can_max: bool):
        self._can_max = can_max

    @property
    def can_z(self) -> bool:
        return self._can_z

    @can_z.setter
    def can_z(self, can_z: bool):
        self._can_z = can_z

    @property
    def max(self) -> bool:
        return self._max

    @max.setter
    def max(self, max: bool):
        if not self._can_max:
            raise ValueError("Can not max")
        else:
            self._max = max

    # ---------------------------------- String ---------------------------------- #

    def __repr__(self) -> str:
        return f"({hex(id(self))}) {self}"

    def __str__(self) -> str:
        return "; ".join(map(str, self.moves))

    # ----------------------------------- Copy ----------------------------------- #

    def clone(self) -> MoveSet:
        clone = MoveSet()
        clone._moves = [move.clone() for move in self._moves]
        clone._max_moves = [move.clone() for move in self._max_moves]
        clone._zmoves = [move.clone() for move in self._zmoves]
        clone._moves_name = dict(**self._moves_name)
        clone._max_moves_name = dict(**self._max_moves_name)
        clone._zmoves_name = dict(**self._zmoves_name)
        clone._can_max = self._can_max
        clone._can_z = self._can_z
        return clone

    def add(self, name, used=True):
        if name in self.moves_name:
            self.moves[self.moves_name[name]].pp -= 1
            if name in self._moves_to_max_moves:
                index = self.max_moves_name[self._moves_to_max_moves[name]]
                self.max_moves[index].pp -= 1
        elif name in self.max_moves_name:
            self.max_moves[self.max_moves_name[name]].pp -= 1
            if name in self._max_moves_to_moves:
                index = self.moves_name[self._max_moves_to_moves[name]]
                self.moves[index].pp -= 1
        elif name in self.zmoves_name:
            self.zmoves[self.zmoves_name[name]].pp -= 1
            self.can_z = False
        move_dict: Dict = MoveDB.db_name.get[name]
        move = Move(move_dict["id"], name, move_dict["pp"], move_dict["target"])
        if "isMax" in move_dict:
            move._type = "max"
            self.max_moves.append(move)
            if used:
                self.max_moves_name[move.name] = len(self.max_moves) - 1
        elif "isZ" in move_dict:
            move._type = "zmove"
            self.zmoves.append(move)
            if used:
                self.zmoves_name[move.name] = len(self.zmoves) - 1
                self.can_z = False
        else:
            self.moves.append(move)
            if used:
                self.moves_name[move.name] = len(self.moves) - 1
