from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict, cast

from pkmai.battle.move import Move


class MovesData(TypedDict, total=False):
    normal: List[Move]
    max: List[Move]
    z: List[Optional[Move]]


@dataclass
class Moveset:
    moves: MovesData = field(default_factory=lambda: MovesData())

    def __index(
        self, name: str, mtype: Literal["normal", "max", "z"] | None = None
    ) -> Tuple[int, Move] | Tuple[None, None]:
        mtypes = [mtype] if mtype else ["normal", "max", "z"]
        for type in mtypes:
            if type in self.moves:
                for index, move in enumerate(self.moves[type]):
                    if move and move.name == name:
                        return (index, move)
        return None, None

    def move_from_recv(
        self, name: str, mtype: Literal["normal", "max", "z"] | None = None
    ):
        _, move = self.__index(name, mtype)
        if not move:
            move = Move(name)
            self.moves[move.type].append(move)

    def move_from_request(self, move_list: List[Dict | str | None]):
        for move_data in move_list:
            if not move_data:
                self.moves["z"].append(None)
                continue
            move_dict: Dict[str, Any] = (
                {"move": move_data} if isinstance(move_data, str) else move_data
            )
            index, move = self.__index(move_dict["move"])
            if not index or not move:
                move = Move(move_dict["move"])
                if move.type not in self.moves:
                    self.moves[move.type] = cast(List[Move], [])
                self.moves[move.type].append(move)
                index = len(self.moves) - 1
            if "pp" in move_dict:
                pp = move_dict["pp"]
                self.moves["normal"][index].pp = pp
                if "max" in self.moves:
                    self.moves["max"][index].pp = pp
                if "z" in self.moves:
                    zmove = self.moves["z"][index]
                    if zmove:
                        zmove.pp = pp
            if "disable" in move_dict:
                disable = move_dict["disable"]
                self.moves["normal"][index].disable = disable
                if "max" in self.moves:
                    self.moves["max"][index].disable = disable
                if "z" in self.moves:
                    zmove = self.moves["z"][index]
                    if zmove:
                        zmove.disable = disable
