from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from pkmai.battle.pokemon import Pokemon, PokemonParser


@dataclass
class Team:
    pokemons: List[Pokemon] = field(default_factory=list)
    positions: Dict[str, int] = field(default_factory=dict, repr=False)
    actives: Dict[int, int] = field(default_factory=dict, repr=False)

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
        self.positions[pos] = index
        self.actives[index] = ord(pos) - ord("a")

    def pokemon_from_request(self, pokemon_request: Dict[str, Any]):
        active_index = 0
        for pokemon_dict in pokemon_request["side"]["pokemon"]:
            name, _, _ = PokemonParser.parse_detail(pokemon_dict["details"])
            index, pokemon = self.__index(name)
            if not pokemon:
                pokemon = Pokemon(name, pokemon_request=pokemon_dict)
                self.pokemons.append(pokemon)
            else:
                pokemon.pokemon_from_request(pokemon_dict)
            if pokemon_dict["active"]:
                if index not in self.actives:
                    pokemon.active_from_request(pokemon_request["active"][active_index])
                    active_index += 1
                else:
                    pokemon.active_from_request(
                        pokemon_request["active"][self.actives[index]]
                    )
