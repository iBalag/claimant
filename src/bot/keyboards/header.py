from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from repository import Repository


def get_regions_list_kb() -> ReplyKeyboardMarkup:
    repository: Repository = Repository()
    regions: List[dict] = repository.get_regions_list()
    regions_list_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    for region in regions:
        region_btn: KeyboardButton = KeyboardButton(f"/регион {region['name']}")
        regions_list_kb.add(region_btn)

    return regions_list_kb
