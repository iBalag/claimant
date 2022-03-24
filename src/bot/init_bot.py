import json
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from repository import Repository


def init_bot(token: str) -> Dispatcher:
    init_db()
    storage: MemoryStorage = MemoryStorage()
    bot: Bot = Bot(token=token)
    dp: Dispatcher = Dispatcher(bot, storage=storage)
    return dp


def init_db():
    repository: Repository = Repository()

    # init regions
    if not repository.is_collection("regions"):
        with open("resources/regions.json") as regions_file:
            regions_info: List[dict] = json.load(regions_file)
            for region in regions_info:
                repository.insert_item("regions", region)

    # init default template
    if not repository.is_collection("claim-tmps"):
        with open("resources/claim_templates/reinstatement.json") as claim_tmp_file:
            claim_tmp_info: dict = json.load(claim_tmp_file)
            repository.insert_item("claim-tmps", claim_tmp_info)

        with open("resources/claim_templates/wages_recovery.json") as claim_tmp_file:
            claim_tmp_info: dict = json.load(claim_tmp_file)
            repository.insert_item("claim-tmps", claim_tmp_info)
