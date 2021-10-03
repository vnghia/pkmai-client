from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, List, Tuple

from pkmai.battle.move import Move
from pkmai.battle.pokemon import Pokemon, PokemonParser


@dataclass
class Team:
    active_size: InitVar[int] = 1
    actives: List[int] = field(default_factory=list)
    pokemons: List[Pokemon] = field(default_factory=list)

    def __post_init__(self, active_size: int = 1):
        self.actives = self.actives or [-1] * active_size

    def __index(self, name: str) -> Tuple[int, Pokemon] | Tuple[None, None]:
        if type in self.pokemons:
            for index, pokemon in enumerate(self.pokemons):
                if pokemon.name == name:
                    return (index, pokemon)
        return None, None

    # ---------------------------------- Message --------------------------------- #

    def add_other_player_pokemon_from_message(
        self, pos: str, nickname: str, detail: str, condition: str
    ):
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

    # ---------------------------------- Request --------------------------------- #

    @classmethod
    def init_from_request(cls, request: Dict[str, Any]) -> Team:
        pokemons: List[Pokemon] = [
            Pokemon.init_from_pokemon_request(pokemon_request)
            for pokemon_request in request["side"]["pokemon"]
        ]
        actives: List[int] = []
        if "active" in request:
            for index, active_request in enumerate(request["active"]):
                actives.append(index)
                pokemons[index].update_attr_from_active_request(active_request)
        return cls(pokemons=pokemons)

    # ---------------------------------- Choose ---------------------------------- #

    def list_all_possible_choices(self) -> Dict[str, Pokemon | Move]:
        choices: Dict[str, Pokemon | Move] = {}
        choices.update(
            {
                f"switch {index + 1 + len(self.actives)}": pokemon
                for index, pokemon in enumerate(self.pokemons[len(self.actives) :])
            }
        )
        for pokemon in self.pokemons:
            choices.update(pokemon.list_all_possible_choices())
        return choices
