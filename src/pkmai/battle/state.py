from __future__ import annotations

from typing import Dict, List

from pkmai.battle.pokemon import Pokemon


class State:
    def __init__(
        self,
        pokemons: Dict[str, Pokemon] = None,
        opponents: Dict[str, Pokemon] = None,
        positions: List[str] = None,
    ) -> None:
        self._pokemons = pokemons or {}
        self._opponents = opponents or {}
        self._positions = positions or []

    @property
    def pokemons(self) -> Dict[str, Pokemon]:
        return self._pokemons

    @property
    def opponents(self) -> Dict[str, Pokemon]:
        return self._opponents

    @property
    def positions(self) -> List[str]:
        return self._positions
