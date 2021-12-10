from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import repository


def get_regions_list_kb() -> ReplyKeyboardMarkup:
    regions: List[dict] = repository.get_regions_list()
    regions_list_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    for region in regions:
        region_btn: KeyboardButton = KeyboardButton(f"/регион {region['name']}")
        regions_list_kb.add(region_btn)

    return regions_list_kb
