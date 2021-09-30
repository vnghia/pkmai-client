import abc
from typing import List, Literal, Union

from pkmai.utils.type import PokemonData, ActiveData


class Choose(abc.ABC):
    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self}"


class SinglePokemonChoose(Choose):
    def __init__(
        self,
        move_spec: Union[str, int],
        move_target: int = 0,
        move_type: Literal["", "mega", "zmove", "max"] = "",
    ) -> None:
        super().__init__()
        self.move_spec = move_spec
        self.move_target = f"{move_target:+}" if move_target != 0 else ""
        self.move_type = move_type

    def __str__(self) -> str:
        return f"move {self.move_spec} {self.move_target} {self.move_type}"


class SwitchChoose(Choose):
    def __init__(
        self,
        switch_spec: Union[str, int],
    ) -> None:
        super().__init__()
        self.switch_spec = switch_spec

    def __str__(self) -> str:
        return f"switch {self.switch_spec}"


def parse_switch_choose(pokemons: List[PokemonData]) -> List[SwitchChoose]:
    chooses: List[SwitchChoose] = []
    for pokemon in pokemons:
        if pokemon["status"] != "fnt":
            chooses.append(SwitchChoose(pokemon["species"]))
    return chooses


def parse_pokemon_choose(active: ActiveData) -> List[SinglePokemonChoose]:
    chooses: List[SinglePokemonChoose] = []
    # TODO(vnghia): ZMove
    for move in active["moves"]:
        chooses.append(SinglePokemonChoose(move["move"]))
        if active.get("can_dynamax"):
            chooses.append(SinglePokemonChoose(move["move"], move_type="max"))
        if active.get("can_mega_evo"):
            chooses.append(SinglePokemonChoose(move["move"], move_type="mega"))
    return chooses
