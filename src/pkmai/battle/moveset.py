from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple, TypedDict

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
    ) -> Tuple[str, int, Move] | Tuple[None, None, None]:
        if mtype:
            for index, move in enumerate(self.moves[mtype]):
                if move and move.name == name:
                    return (name, index, move)
        else:
            for index, move in enumerate(self.moves["normal"]):
                if move.name == name:
                    return (name, index, move)
            for index, move in enumerate(self.moves["max"]):
                if move.name == name:
                    return (name, index, move)
            for index, move in enumerate(self.moves["z"]):
                if move and move.name == name:
                    return (name, index, move)
        return None, None, None

    def move_from_recv(
        self, name: str, mtype: Literal["normal", "max", "z"] | None = None
    ):
        _, _, move = self.__index(name, mtype)
        if not move:
            move = Move(name, init_by_name=True)
            self.moves[move.type].append(move)

    def move_from_request(
        self,
        move_list: List[Optional[Dict]],
        mtype: Literal["normal", "max", "z"],
    ):
        if mtype not in self.moves:
            if mtype == "normal":
                self.moves["normal"] = []
            elif mtype == "max":
                self.moves["max"] = []
            else:
                self.moves["z"] = []
        for move_dict in move_list:
            if not move_dict:
                if mtype == "z":
                    self.moves["z"].append(None)
                continue
            _, index, move = self.__index(move_dict["move"], mtype)
            if not index or not move:
                move = Move(move_dict["move"], init_by_name=(mtype != "max"))
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
