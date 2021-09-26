from typing import Callable, List, Literal, TypedDict


class GlobalData(TypedDict, total=False):
    challstr: str
    username: str


ListernerT = Callable[[List[str]], None]


# ---------------------------------- Battle ---------------------------------- #


class PlayerData(TypedDict, total=False):
    name: str
    rating: int
    teamsize: int


class MoveData(TypedDict, total=False):
    move: str
    id: str
    pp: int
    maxpp: int
    target: Literal["normal", "self", "adjacentFoe"]
    disable: bool


class MaxMoveData(TypedDict, total=False):
    move: str
    target: Literal["self", "adjacentFoe"]


class PokemonStat(TypedDict, total=False):
    atk: int
    defense: int
    spa: int
    spd: int
    spe: int


class PokemonData(TypedDict, total=False):
    ident: str
    species: str
    level: int
    gender: Literal["M", "F"]
    current_hp: int
    total_hp: int
    active: bool
    stats: PokemonStat
    moves: List[str]
    base_ability: str
    item: str
    pokeball: str
    ability: str


class ActiveData(TypedDict, total=False):
    moves: List[MoveData]
    can_dynamax: bool
    max_moves: List[MaxMoveData]


class SideData(TypedDict, total=False):
    name: str
    id: str
    pokemons: List[PokemonData]


class RequestData(TypedDict, total=False):
    force_switch: bool
    active: ActiveData
    side: SideData
    no_cancel: bool
    rqid: int
