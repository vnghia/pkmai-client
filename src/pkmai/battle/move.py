from typing import Dict, Literal


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
        type: Literal["", "mega", "zmove", "max"] = "",
    ) -> None:
        self._name = name
        self._id = id
        self._pp = maxpp
        self._maxpp = maxpp
        self._target = target
        self._type = type
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
    def type(self) -> Literal["", "mega", "zmove", "max"]:
        return self._type

    @property
    def disable(self) -> bool:
        return self._disable

    # ---------------------------------- String ---------------------------------- #

    def __repr__(self) -> str:
        return f"({hex(id(self))}) {self}"

    def __str__(self) -> str:
        return self.name if self.name else self.id

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
