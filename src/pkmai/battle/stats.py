from __future__ import annotations

from typing import Dict


class Stats:
    def __init__(
        self, atk: int = 0, def_: int = 0, spa: int = 0, spd: int = 0, spe: int = 0
    ) -> None:
        self._atk = atk
        self._def = def_
        self._spa = spa
        self._spd = spd
        self._spe = spe
        self._boost_atk = 1.0
        self._boost_def = 1.0
        self._boost_spa = 1.0
        self._boost_spd = 1.0
        self._boost_spe = 1.0

    @property
    def atk(self) -> int:
        if not self._atk:
            raise ValueError("atk is empty")
        return int(self._atk * self._boost_atk)

    @atk.setter
    def atk(self, atk: int):
        self._boost_atk = atk / self._atk

    @property
    def def_(self) -> int:
        if not self._def:
            raise ValueError("def is empty")
        return int(self._def * self._boost_def)

    @def_.setter
    def def_(self, def_: int):
        self._boost_def = def_ / self._def

    @property
    def spa(self) -> int:
        if not self._spa:
            raise ValueError("spa is empty")
        return int(self._spa * self._boost_spa)

    @spa.setter
    def spa(self, spa: int):
        self._boost_spa = spa / self._spa

    @property
    def spd(self) -> int:
        if not self._spd:
            raise ValueError("spd is empty")
        return int(self._spd * self._boost_spd)

    @spd.setter
    def spd(self, spd: int):
        self._boost_spd = spd / self._spd

    @property
    def spe(self) -> int:
        if not self._spe:
            raise ValueError("spe is empty")
        return int(self._spe * self._boost_spe)

    @spe.setter
    def spe(self, spe: int):
        self._boost_spe = spe / self._spe

    @property
    def boost_atk(self) -> float:
        return self._boost_atk

    @boost_atk.setter
    def boost_atk(self, coff: float):
        self._boost_atk = coff

    @property
    def boost_def(self) -> float:
        return self._boost_def

    @boost_def.setter
    def boost_def(self, coff: float):
        self._boost_def = coff

    @property
    def boost_spa(self) -> float:
        return self._boost_spa

    @boost_spa.setter
    def boost_spa(self, coff: float):
        self._boost_spa = coff

    @property
    def boost_spd(self) -> float:
        return self._boost_spd

    @boost_spd.setter
    def boost_spd(self, coff: float):
        self._boost_spd = coff

    @property
    def boost_spe(self) -> float:
        return self._boost_spe

    @boost_spe.setter
    def boost_spe(self, coff: float):
        self._boost_spe = coff

    @classmethod
    def create_from_request(cls, stats_dict: Dict) -> Stats:
        return cls(
            stats_dict["atk"],
            stats_dict["def"],
            stats_dict["spa"],
            stats_dict["spd"],
            stats_dict["spe"],
        )

    # ---------------------------------- Request --------------------------------- #

    def update_from_request(self, stats_dict: Dict):
        if self.atk != stats_dict["atk"]:
            self.atk = int(stats_dict["atk"])
        if self.def_ != stats_dict["def"]:
            self.def_ = int(stats_dict["def"])
        if self.spa != stats_dict["spa"]:
            self.spa = int(stats_dict["spa"])
        if self.spd != stats_dict["spd"]:
            self.spd = int(stats_dict["spd"])
        if self.spe != stats_dict["spe"]:
            self.spe = int(stats_dict["spe"])
