from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, List, Tuple

from pkmai.battle.pokemon import Pokemon, PokemonParser


@dataclass
class Team:
    active_size: InitVar[int]
    actives: List[int] = field(default_factory=list)
    pokemons: List[Pokemon] = field(default_factory=list)

    def __post_init__(self, active_size: int):
        self.actives = self.actives or [-1] * active_size

    def __index(self, name: str) -> Tuple[int, Pokemon] | Tuple[None, None]:
        if type in self.pokemons:
            for index, pokemon in enumerate(self.pokemons):
                if pokemon.name == name:
                    return (index, pokemon)
        return None, None

    def pokemon_from_recv(self, pos: str, nickname: str, detail: str, condition: str):
        name, gender, level = PokemonParser.parse_detail(detail)
        index, pokemon = self.__index(name)
        if not index or not pokemon:
            pokemon = Pokemon(name)
            pokemon.nickname = nickname
            pokemon.gender = gender
            pokemon.level = level
            self.pokemons.append(pokemon)
            index = len(self.pokemons) - 1
        current_hp, total_hp, status = PokemonParser.parse_condition(condition)
        pokemon.current_hp = current_hp
        pokemon.total_hp = pokemon.total_hp or total_hp
        pokemon.status = status
        self.actives[ord(pos) - ord("a")] = index

    @classmethod
    def from_request(cls, pokemon_request: Dict[str, Any]) -> Team:
        pokemons: List[Pokemon] = []
        actives: List[int] = []
        for index, pokemon_dict in enumerate(pokemon_request["side"]["pokemon"]):
            name, _, _ = PokemonParser.parse_detail(pokemon_dict["details"])
            pokemon = Pokemon(name, pokemon_request=pokemon_dict)
            pokemons.append(pokemon)
            if pokemon_dict["active"]:
                actives.append(index)
                pokemon.active_from_request(pokemon_request["active"][len(actives) - 1])
        return cls(len(actives), actives, pokemons)
