from __future__ import annotations

from typing import Dict, List, Tuple

from pkmai.battle.pokemon import Pokemon


class Request:
    def __init__(
        self,
        pokemons: Dict[Tuple[str, str], Pokemon],
        positions: List[Tuple[str, str]],
        rqid: int,
        actives: List[int],
        trappeds: List[bool],
        force_switchs: List[bool],
        no_cancel: bool,
        wait: bool,
    ) -> None:
        self._pokemons = pokemons
        self._positions = positions
        self._rqid = rqid
        self._actives = actives
        self._trappeds = trappeds
        self._force_switchs = force_switchs
        self._no_cancel = no_cancel
        self._wait = wait

    @property
    def pokemons(self) -> Dict[Tuple[str, str], Pokemon]:
        return self._pokemons

    @property
    def positions(self) -> List[Tuple[str, str]]:
        return self._positions

    @property
    def rqid(self) -> int:
        return self._rqid

    @property
    def actives(self) -> List[int]:
        return self._actives

    @property
    def trappeds(self) -> List[bool]:
        return self._trappeds

    @property
    def force_switchs(self) -> List[bool]:
        return self._force_switchs

    @property
    def no_cancel(self) -> bool:
        return self._no_cancel

    @property
    def wait(self) -> bool:
        return self._wait

    @classmethod
    def create(cls, request: Dict) -> Request:
        rqid = request["rqid"]
        pokemons: Dict[Tuple[str, str], Pokemon] = {}
        positions: List[Tuple[str, str]] = []
        actives: List[int] = []
        trappeds: List[bool] = []
        for idx, pokemon_dict in enumerate(request["side"]["pokemon"]):
            pokemon = Pokemon.create_from_request(pokemon_dict, idx)
            if pokemon_dict["active"] and "active" in request:
                actives.append(idx)
                active_dict = request["active"][len(actives) - 1]
                trappeds.append("trapped" in active_dict)
                pokemon.update_active_from_request(active_dict)
            pokemons[(pokemon.player_id, pokemon.name)] = pokemon
            positions.append((pokemon.player_id, pokemon.name))
        force_switchs = request.get("forceSwitch", [False] * len(actives))
        no_cancel = "noCancel" in request
        wait = "wait" in request
        return cls(
            pokemons, positions, rqid, actives, trappeds, force_switchs, no_cancel, wait
        )
