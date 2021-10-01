from typing import Dict
import requests


def read_json_from_pkm_server(url: str) -> Dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


class MoveDB:
    db_id: Dict = read_json_from_pkm_server(
        "https://play.pokemonshowdown.com/data/moves.json"
    )
    db_name: Dict = {move["name"]: dict(id=id, **move) for id, move in db_id.items()}
