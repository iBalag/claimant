import json
from typing import List

from repository import Repository

repository = Repository()

# themes = repository.get_tmps_list()
# print(themes)

# with open("../../resources/regions.json") as f:
#     regions_raw: List[dict] = json.load(f)
#     for r in regions_raw:
#         repository.insert_item("regions", r)

code = repository.get_region_code("153015")
print(code)