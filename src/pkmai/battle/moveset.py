from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict, cast

from pkmai.battle.db import MoveDB
from pkmai.battle.move import Move


class MovesData(TypedDict, total=False):
    normal: List[Move]
    max: List[Move]
    z: List[Optional[Move]]


@dataclass
class Moveset:
    moves: MovesData = field(default_factory=lambda: MovesData())
    is_max: bool = False
    can_max: bool = False
    can_z: bool = False

    # ---------------------------------- Manager --------------------------------- #

    def __index_move(
        self, name_or_id: str, type: Literal["normal", "max", "z"] | None = None
    ) -> Tuple[str, int, Move] | Tuple[str, None, None]:
        id = MoveDB.to_id(name_or_id)
        types = [type] if type else ["normal", "max", "z"]
        for type in types:
            if type in self.moves:
                for index, move in enumerate(self.moves[type]):
                    if move and move.id == id:
                        return (id, index, move)
        return id, None, None

    def __upsert_move(
        self, name_or_id: str, type: Literal["normal", "max", "z"] | None = None
    ) -> Tuple[str, int, Move]:
        id, index, move = self.__index_move(name_or_id, type)
        if not index or not move:
            move = Move(id)
            if type and move.type != type:
                raise ValueError((type, move.type))
            if move.type not in self.moves:
                self.moves[move.type] = cast(List[Move], [])
            self.moves[move.type].append(move)
            index = len(self.moves[move.type]) - 1
        return id, index, move

    # ---------------------------------- Message --------------------------------- #

    def add_other_player_move_from_message(self, name: str, pressured: bool = False):
        if name == "Struggle":
            pass
        _, _, move = self.__upsert_move(name)
        move.pp -= 1 + bool(pressured)

    # ---------------------------------- Request --------------------------------- #

    def update_attr_all_move_types(self, index: int, attr: str, value: Any):
        self.moves["normal"][index].__dict__[attr] = value
        if "max" in self.moves:
            self.moves["max"][index].__dict__[attr] = value
        if "z" in self.moves:
            zmove = self.moves["z"][index]
            if zmove:
                zmove.__dict__[attr] = value

    def update_attr_all_move_types_from_normal_move_request(
        self, index: int, move_request: Dict[str, Any]
    ):
        if "pp" in move_request:
            self.update_attr_all_move_types(index, "pp", move_request["pp"])
        if "disable" in move_request:
            self.update_attr_all_move_types(index, "disable", move_request["disable"])

    def update_attr_all_move_types_from_active_move_list_request(
        self,
        move_list_request: List[Dict[str, Any]],
    ):
        map(
            self.update_attr_all_move_types_from_normal_move_request,
            *enumerate(move_list_request),
        )

    def init_special_move_types_from_active_request(
        self,
        move_list_request: List[Dict[str, Any] | None],
        type: Literal["max", "z"],
    ):
        self.moves[type] = [
            Move(move_request["move"]) if move_request else None
            for move_request in move_list_request
        ]

    def init_all_move_types_from_active_request(self, active_request: Dict[str, Any]):
        can_max = "canDynamax" in active_request
        can_z = "canZMove" in active_request
        has_max = "maxMoves" in active_request
        is_max = True if has_max and not can_max else False
        if has_max:
            self.init_special_move_types_from_active_request(
                active_request["maxMoves"]["maxMoves"], "max"
            )
        if can_z:
            self.init_special_move_types_from_active_request(
                active_request["canZMove"], "z"
            )
        self.update_attr_all_move_types_from_active_move_list_request(
            active_request["moves"]
        )
        self.can_max = can_max
        self.can_z = can_z
        self.is_max = is_max

    @classmethod
    def init_normal_move_from_move_list_request(cls, move_list_request: List[str]):
        normal_moves: List[Move] = [Move(id) for id in move_list_request]
        return cls(MovesData(normal=normal_moves))
