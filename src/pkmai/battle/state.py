from __future__ import annotations

from typing import Dict, List, Tuple

from pkmai.battle.pokemon import Pokemon


class State:
    def __init__(
        self,
        pokemons: List[Pokemon] = None,
        active_pokemons: Dict[Tuple[str, str, str], Pokemon] = None,
        opponents: List[Pokemon] = None,
        active_opponents: Dict[Tuple[str, str, str], Pokemon] = None,
        positions: List[str] = None,
    ) -> None:
        self._pokemons = pokemons or []
        self._active_pokemons = active_pokemons or {}
        self._opponents = opponents or []
        self._active_opponents = active_opponents or {}
        self._positions = positions or []

    @property
    def pokemons(self) -> List[Pokemon]:
        return self._pokemons

    @property
    def active_pokemons(self) -> Dict[Tuple[str, str, str], Pokemon]:
        return self._active_pokemons

    @property
    def opponents(self) -> List[Pokemon]:
        return self._opponents

    @property
    def active_opponents(self) -> Dict[Tuple[str, str, str], Pokemon]:
        return self._active_opponents

    @property
    def positions(self) -> List[str]:
        return self._positions
