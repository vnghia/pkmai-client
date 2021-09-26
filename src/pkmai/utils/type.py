from typing import Callable, List, TypedDict


class GlobalData(TypedDict, total=False):
    challstr: str
    username: str


class PlayerData(TypedDict, total=False):
    name: str
    rating: int
    teamsize: int


ListernerT = Callable[[List[str]], None]
