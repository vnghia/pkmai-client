from __future__ import annotations

from typing import Dict, List, Tuple

from pkmai.battle.pokemon import Pokemon


class State:
    def __init__(
        self,
        pokemons: Dict[Tuple[str, str, int], Pokemon] = None,
        active_pokemons: Dict[str, Tuple[str, str, int]] = None,
        opponents: Dict[str, Dict[str, Pokemon]] = None,
        active_opponents: Dict[str, Dict[str, str]] = None,
        positions: List[str] = None,
    ) -> None:
        self._pokemons = pokemons or {}
        self._active_pokemons = active_pokemons or {}
        self._opponents = opponents or {}
        self._active_opponents = active_opponents or {}
        self._positions = positions or []

    @property
    def pokemons(self) -> Dict[Tuple[str, str, int], Pokemon]:
        return self._pokemons

    @property
    def active_pokemons(self) -> Dict[str, Tuple[str, str, int]]:
        return self._active_pokemons

    @property
    def opponents(self) -> Dict[str, Dict[str, Pokemon]]:
        return self._opponents

    @property
    def active_opponents(self) -> Dict[str, Dict[str, str]]:
        return self._active_opponents

    @property
    def positions(self) -> List[str]:
        return self._positions

    def copy(self) -> State:
        pass
