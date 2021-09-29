from typing import Callable, List, Literal, Optional, TypedDict


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


class SpeicalMoveData(TypedDict, total=False):
    move: str
    target: Literal["self", "adjacentFoe"]


PokemonStat = TypedDict(
    "PokemonStat",
    {"atk": int, "def": int, "spa": int, "spd": int, "spe": int},
    total=False,
)


class PokemonData(TypedDict, total=False):
    ident: str
    species: str
    level: int
    gender: Literal["M", "F", "N"]
    current_hp: int
    total_hp: int
    status: str
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
    max_moves: List[SpeicalMoveData]
    can_mega_evo: bool
    can_z_move: List[Optional[SpeicalMoveData]]


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
