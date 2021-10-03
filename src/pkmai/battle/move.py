from __future__ import annotations

from dataclasses import InitVar, dataclass
from typing import Any, Dict, Literal

from pkmai.battle.db import MoveDB


@dataclass
class Move:
    name_or_id: InitVar[str]
    id: str = ""
    name: str = ""
    accuracy: int | Literal[True] = 0
    base_power: int = 0
    pp: int = 0
    maxpp: int = 0
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
    ] = "normal"
    type: Literal["normal", "max", "z"] = "normal"
    disable: bool = False

    need_additional: InitVar[bool] = True
    move_db: InitVar[Dict[str, Any]] = None

    def __post_init__(
        self,
        name_or_id: str,
        need_additional: bool = True,
        move_db: Dict[str, Any] = None,
    ):
        if need_additional:
            self.load_additional(name_or_id, move_db)

    def load_additional(self, name_or_id: str, move_db: Dict[str, Any] = None):
        move_db = move_db or MoveDB.item(name_or_id)

        self.id = self.id or MoveDB.to_id(name_or_id)
        self.name = self.name or move_db["name"]
        self.accuracy = self.accuracy or move_db["accuracy"]
        self.base_power = self.base_power or move_db["basePower"]
        self.maxpp = self.maxpp or move_db["pp"]
        self.pp = self.maxpp
        self.target = self.target or move_db["target"]
        if "isZ" in move_db:
            self.type = "z"
        elif "isMax" in move_db:
            self.type = "max"
        else:
            self.type = "normal"
