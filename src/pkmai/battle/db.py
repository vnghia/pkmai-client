from __future__ import annotations

from typing import Dict

import requests
from pkmai.utils.string import to_id


def read_json_from_pkm_server(url: str) -> Dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


class DB(type):
    def __init__(cls, name, bases, attrs):
        url = attrs["url"]
        cls.db_id: Dict = read_json_from_pkm_server(url)
        super().__init__(name, bases, attrs)

    def to_id(cls, name_or_id: str) -> str:
        return to_id(name_or_id)

    def item(cls, name_or_id: str) -> Dict:
        id = to_id(name_or_id)
        return cls.db_id[id]


class MoveDB(metaclass=DB):
    url = "https://play.pokemonshowdown.com/data/moves.json"


class PokemonDB(metaclass=DB):
    url = "https://play.pokemonshowdown.com/data/pokedex.json"
