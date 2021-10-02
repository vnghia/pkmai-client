from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass
class Stats:
    boost_ratio: ClassVar[Dict[int, float]] = {
        -6: 1 / 4,
        -5: 1 / 3.5,
        -4: 1 / 3,
        -3: 1 / 2.5,
        -2: 1 / 2,
        -1: 1 / 1.5,
        0: 1.0,
        1: 1.5,
        2: 2,
        3: 2.5,
        4: 3,
        5: 3.5,
        6: 4,
    }
    atk_: int = 0
    def_: int = 0
    spa_: int = 0
    spd_: int = 0
    spe_: int = 0
    boost_atk: int = 1
    boost_def: int = 1
    boost_spa: int = 1
    boost_spd: int = 1
    boost_spe: int = 1

    def read(self, key: str) -> int:
        return int(
            self.__dict__[f"{key}_"] * self.boost_ratio[self.__dict__[f"boost_{key}"]]
        )

    def boost(self, key: str, stage: int):
        self.__dict__[f"boost_{key}"] += stage

    def reset(self):
        for key in ["atk", "def", "spa", "spd", "spe"]:
            self.__dict__[f"boost_{key}"] = 1

    def stats_from_request(self, stats_dict: Dict):
        self.reset()
        for key, value in stats_dict:
            self.__dict__[f"{key}_"] = value
