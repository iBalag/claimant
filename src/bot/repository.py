import json
from typing import List


def get_tmps_list() -> List[str]:
    # TODO: get template names from DB
    tmp_names: List[str] = ["взыскание заработной платы", "восстановление на рабочем месте"]
    return tmp_names


def get_regions_list() -> List[dict]:
    # TODO: get regions from DB
    with open("../../resources/regions.json") as f:
        regions: List[dict] = json.load(f)
        return regions
