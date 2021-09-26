from typing import Callable, List, TypedDict


class GlobalData(TypedDict, total=False):
    challstr: str
    username: str


ListernerT = Callable[[List[str]], None]
