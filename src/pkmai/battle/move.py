from __future__ import annotations

from dataclasses import InitVar, dataclass
from typing import Any, Dict, Literal

from pkmai.battle.db import MoveDB


@dataclass
class Move:
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

    init_by_name: InitVar[bool] = False
    data_from_dict: InitVar[bool] = True
    move_dict: InitVar[Dict[str, Any]] = None

    def __post_init__(
        self,
        init_by_name: bool = False,
        data_from_dict: bool = True,
        move_dict: Dict[str, Any] = None,
    ):
        if data_from_dict:
            self.load_from_dict(self, init_by_name, move_dict)

    @staticmethod
    def load_from_dict(
        move: Move, init_by_name: bool = False, move_dict: Dict[str, Any] = None
    ):
        move_dict = move_dict or (
            MoveDB.db_id[move.id] if not init_by_name else MoveDB.db_name[move.name]
        )
        move.id = move.id or move_dict["id"]
        move.name = move.name or move_dict["name"]
        move.accuracy = move.accuracy or move_dict["accuracy"]
        move.base_power = move.base_power or move_dict["basePower"]
        move.maxpp = move.maxpp or move_dict["pp"]
        move.pp = move.maxpp
        move.target = move.target or move_dict["target"]
        if "isZ" in move_dict:
            move.type = "z"
        elif "isMax" in move_dict:
            move.type = "max"
        else:
            move.type = "normal"
