import traceback
from typing import List


def get_traceback(exce: BaseException) -> str:
    return "".join(traceback.format_exception(type(exce), exce, exce.__traceback__))


def raise_from_message(msg: List[str]):
    if msg[0] == "namerequired":
        raise PermissionError(msg[1])
    elif msg[0] == "nonexistent":
        raise KeyError(msg[1])
