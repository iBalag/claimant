from typing import List

from dotenv import dotenv_values
from pymongo import MongoClient


class Repository:
    def __init__(self):
        self.config = dotenv_values(".env")

    def _get_mongo_client(self):
        return MongoClient(
            host=self.config["MONGO_HOST"],
            port=int(self.config["MONGO_PORT"]),
            username=self.config["MONGO_INITDB_USERNAME"],
            password=self.config["MONGO_INITDB_PASSWORD"],
            authSource="claimant",
            authMechanism='SCRAM-SHA-256'
        )

    def get_tmps_list(self) -> List[str]:
        with self._get_mongo_client() as client:
            tmps: List[dict] = list(client["claimant"]["claim-tmps"].find({}, {"theme": 1, "_id": 0}))
            return [tmp["theme"] for tmp in tmps]

    def get_region_code(self, post_code: str) -> str:
        post_code_prefix: str = post_code[:3]
        with self._get_mongo_client() as client:
            result = list(client["claimant"]["regions"].find({"post": post_code_prefix}))
            if len(result) > 0:
                return result[0]["code"]
            return "-1"

    def insert_item(self, collection_name: str, item: dict):
        with self._get_mongo_client() as client:
            client["claimant"][collection_name].insert_one(item)