from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from keyboards import emojis
from repository import Repository


PART_NAMES: List[str] = ["head", "story", "essence", "proofs", "claims", "additions"]


def get_claim_parts_kb(user_id: int) -> ReplyKeyboardMarkup:
    parts_status: dict = get_claim_parts_status(user_id)
    claim_parts_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    claim_parts_kb\
        .add(KeyboardButton(f"{emojis.top_hat} шапка {emojis.check_mark if parts_status['head'] is True else ''}")) \
        .add(KeyboardButton(f"{emojis.speech_balloon} фабула {emojis.check_mark if parts_status['story'] is True else ''}")) \
        .add(KeyboardButton(f"{emojis.key} суть нарушения {emojis.check_mark if parts_status['essence'] is True else ''}")) \
        .add(KeyboardButton(f"{emojis.page_with_curl} доказательства {emojis.check_mark if parts_status['proofs'] is True else ''}")) \
        .add(KeyboardButton(f"{emojis.index_pointing_up} требования {emojis.check_mark if parts_status['claims'] is True else ''}")) \
        .add(KeyboardButton(f"{emojis.card_index_dividers} приложения {emojis.check_mark if parts_status['additions'] is True else ''}"))

    claim_parts_kb.row(*[KeyboardButton(f"{emojis.left_arrow} к шаблонам"),
                         KeyboardButton(f"{emojis.inbox_tray} получить")])
    return claim_parts_kb


def get_claim_parts_status(user_id: int) -> dict:
    repository: Repository = Repository()
    claim_data: dict = repository.get_claim_data(user_id)
    if "claim_data" not in claim_data.keys():
        return {pn: False for pn in PART_NAMES}
    parts_status: dict = {}
    for part_name in PART_NAMES:
        if part_name in claim_data["claim_data"].keys():
            parts_status.update(**{part_name: True})
        else:
            parts_status.update(**{part_name: False})
    return parts_status
