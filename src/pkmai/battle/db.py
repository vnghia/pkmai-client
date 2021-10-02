from typing import Dict
import requests


def read_json_from_pkm_server(url: str) -> Dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


class DB(type):
    def __init__(cls, name, bases, attrs):
        url = attrs["url"]
        cls.db_id: Dict = read_json_from_pkm_server(url)
        cls.db_name: Dict = {
            move["name"]: dict(id=id, **move) for id, move in cls.db_id.items()
        }
        super().__init__(name, bases, attrs)

    @classmethod
    def to_id(cls, name_or_id: str) -> str:
        if name_or_id in cls.db_id:
            return name_or_id
        else:
            return cls.db_name[name_or_id]["id"]

    @classmethod
    def to_name(cls, name_or_id: str) -> str:
        if name_or_id in cls.db_name:
            return name_or_id
        else:
            return cls.db_id[name_or_id]["name"]


class MoveDB(metaclass=DB):
    url = "https://play.pokemonshowdown.com/data/moves.json"


class PokemonDB(metaclass=DB):
    url = "https://play.pokemonshowdown.com/data/pokedex.json"
