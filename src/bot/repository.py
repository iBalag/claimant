from datetime import datetime
from typing import List, Optional, Set, Callable

from bson import ObjectId
from cryptography.fernet import Fernet

from dotenv import dotenv_values
from pymongo import MongoClient, DESCENDING

import bot_config


class Repository:
    def __init__(self):
        if bot_config.ENV == "prod":
            self.config = dotenv_values(".env")
        if bot_config.ENV == "dev":
            self.config = dotenv_values(".env-dev")

        self.db_name: str = self.config["MONGO_INITDB_DATABASE"]
        self.key: str = self.config["ENCRYPT_KEY"]
        self.fernet: Fernet = Fernet(self.key)
        self.sensitive_fields: Set[str] = {"user_name", "user_post_code", "chosen_city", "chosen_street",
                                           "house_chosen", "apartment_chosen"}

    def _get_mongo_client(self):
        return MongoClient(
            host=self.config["MONGO_HOST"],
            port=int(self.config["MONGO_PORT"]),
            username=self.config["MONGO_INITDB_USERNAME"],
            password=self.config["MONGO_INITDB_PASSWORD"],
            authSource=self.db_name,
            authMechanism="SCRAM-SHA-256"
        )

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()

    def process_data(self, data: dict, processor: Callable[[str], str]) -> dict:
        for key, value in data.items():
            if key in self.sensitive_fields and isinstance(value, str):
                data[key] = processor(value)
            if isinstance(value, dict):
                data[key] = self.process_data(value, processor)
        return data

    def get_tmps_list(self) -> List[str]:
        with self._get_mongo_client() as client:
            tmps: List[dict] = list(client[self.db_name]["claim-tmps"].find({}, {"theme": 1, "_id": 0}))
            return [tmp["theme"] for tmp in tmps]

    def get_region_code(self, post_code: str) -> str:
        post_code_prefix: str = post_code[:3]
        with self._get_mongo_client() as client:
            result = list(client[self.db_name]["regions"].find({"post": post_code_prefix}))
            if len(result) > 0:
                return result[0]["code"]
            return "-1"

    def insert_item(self, collection_name: str, item: dict):
        encrypted_item: dict = self.process_data(item, self.encrypt)
        with self._get_mongo_client() as client:
            client[self.db_name][collection_name].insert_one(encrypted_item)

    def remove_item(self, collection_name: str, item_id: ObjectId):
        with self._get_mongo_client() as client:
            client[self.db_name][collection_name].delete_one({"_id": item_id})

    def get_claim_data(self, user_id: int, claim_theme: Optional[str] = None) -> Optional[dict]:
        find_filter: dict = {"user_id": user_id}
        if claim_theme is not None:
            find_filter.update(**{"claim_theme": claim_theme})

        with self._get_mongo_client() as client:
            search_result = list(client[self.db_name]["claim-data"].find(find_filter))
            # there can be only one :)
            result: dict
            if len(search_result) == 1:
                result = search_result[0]
            if len(search_result) == 0:
                return None
            if len(search_result) > 1:
                # TODO: how to hande this? Take latest?
                result = search_result[0]

            decrypted_item: dict = self.process_data(result, self.decrypt)
            return decrypted_item

    def update_record(self, collection_name: str, item_id: ObjectId, new_value: dict):
        encrypted_value: dict = self.process_data(new_value, self.encrypt)
        with self._get_mongo_client() as client:
            client[self.db_name][collection_name].update_one({"_id": item_id}, {"$set": encrypted_value}, upsert=False)

    def get_current_claim_theme(self, user_id: int) -> Optional[str]:
        result = self.get_claim_data(user_id)
        if result is not None:
            return result["claim_theme"]
        else:
            return None

    def get_claim_tmp(self, claim_theme: str) -> Optional[dict]:
        with self._get_mongo_client() as client:
            result = list(client[self.db_name]["claim-tmps"].find({"theme": claim_theme}))
            # there can be only one :)
            if len(result) == 1:
                return result[0]
            if len(result) == 0:
                return None
            if len(result) > 1:
                # TODO: how to hande this? Take latest?
                return result[0]

    def get_claim_tmp_examples(self, claim_theme: str, part: str) -> Optional[List[str]]:
        claim_tmp: Optional[dict] = self.get_claim_tmp(claim_theme)
        examples: Optional[List[str]] = None
        if claim_tmp is not None and part in claim_tmp.keys() and "examples" in claim_tmp[part].keys():
            examples = claim_tmp[part]["examples"]
        return examples

    def get_claim_tmp_options(self, claim_theme: str, part: str) -> Optional[List[str]]:
        claim_tmp: Optional[dict] = self.get_claim_tmp(claim_theme)
        options: Optional[List[str]] = None
        if claim_tmp is not None and part in claim_tmp.keys() and "options" in claim_tmp[part].keys():
            options = claim_tmp[part]["options"]
        return options

    def get_claim_tmp_actions(self, claim_theme: str, part: str) -> Optional[List[str]]:
        claim_tmp: Optional[dict] = self.get_claim_tmp(claim_theme)
        actions: Optional[List[str]] = None
        if claim_tmp is not None and part in claim_tmp.keys() and "actions" in claim_tmp[part].keys():
            actions = claim_tmp[part]["actions"]
        return actions

    def get_statistics(self, date: datetime) -> Optional[dict]:
        with self._get_mongo_client() as client:
            result = list(client[self.db_name]["statistics"].find({"date": date}))
            # there can be only one :)
            if len(result) == 1:
                return result[0]
            if len(result) == 0:
                return None
            if len(result) > 1:
                # TODO: how to hande this? Take latest?
                return result[0]

    def get_statistics_slice(self, max_days: int = 30) -> List[dict]:
        with self._get_mongo_client() as client:
            result = list(client[self.db_name]["statistics"].find().sort("date", DESCENDING).limit(max_days))
            return result

    def is_collection(self, collection_name: str) -> bool:
        with self._get_mongo_client() as client:
            collections = list(client[self.db_name].list_collections())
            collections_name = [c["name"] for c in collections]
            return True if collection_name in collections_name else False
