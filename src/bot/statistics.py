from datetime import datetime
from typing import Optional

import pytz
from hashlib import blake2b
from aiogram import types
from aiogram.dispatcher import FSMContext

from repository import Repository


def get_user_id_hash(user_id: int) -> str:
    h = blake2b(digest_size=12)
    h.update(user_id.to_bytes(8, byteorder="big"))
    return h.hexdigest()


def count_event(event_name: str, user_id: int):
    repository: Repository = Repository()
    current_date: datetime = datetime.utcnow().replace(tzinfo=pytz.UTC, hour=0, minute=0, second=0, microsecond=0)
    current_stats: Optional[dict] = repository.get_statistics(current_date)
    user_id_hash: str = get_user_id_hash(user_id)
    if current_stats is None:
        new_stats = {
            "date": current_date,
            "unique_users": {
                user_id_hash: {
                    event_name: 1
                }
            }
        }
        repository.insert_item("statistics", new_stats)
        return

    stats_update: dict = {}
    if "unique_users" in current_stats.keys():
        if user_id_hash in current_stats["unique_users"].keys():
            event_count = current_stats["unique_users"][user_id_hash].get(event_name, 0)
            stats_update = {
                f"unique_users.{user_id_hash}.{event_name}": event_count + 1
            }
        else:
            stats_update = {
                f"unique_users.{user_id_hash}": {
                    event_name: 1
                }
            }

    repository.update_record("statistics", current_stats["_id"], stats_update)


def collect_statistic(event_name: str):
    def collect(handler):
        async def wrapper(message: types.Message, state: FSMContext):
            try:
                user_id: int = message.from_user.id
                count_event(event_name, user_id)
            except Exception as ex:
                print(f"Error occurred while collection statistics: {ex}")

            await handler(message, state)
        return wrapper
    return collect
