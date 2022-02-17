from datetime import datetime
from typing import List, Optional, Dict

import pytz
from aiogram import types, Dispatcher
from dotenv import dotenv_values

import bot_config
from repository import Repository


def get_admin_ids() -> List[int]:
    config: dict = {}
    if bot_config.ENV == "prod":
        config = dotenv_values(".env")
    elif bot_config.ENV == "dev":
        config = dotenv_values(".env-dev")

    admin_ids_raw: Optional[str] = config.get("ADMIN_IDS")
    if admin_ids_raw is None:
        return []

    admin_ids_str: List[str] = admin_ids_raw.split(",")
    admin_ids: List[int] = [int(admin_id_str) for admin_id_str in admin_ids_str if admin_id_str.isdigit()]
    return admin_ids


def aggregate_events(stat: List[dict]) -> Dict[datetime, dict]:
    result = {}
    stat.sort(key=lambda s: s["date"])
    for day_stat in stat:
        date = day_stat["date"]
        day_agg = {
            "unique_users": len(day_stat["unique_users"].keys()),
            "events_count": {}
        }
        for user_id_hash, events in day_stat["unique_users"].items():
            for event, count in events.items():
                day_agg["events_count"][event] = day_agg["events_count"].get(event, 0) + count

        result[date] = day_agg

    return result


async def show_statistics(message: types.Message):
    admin_ids: List[int] = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.reply("Данная команда доступна только администраторам бота.")
        return

    arguments = message.get_args()
    repository: Repository = Repository()
    if not arguments:
        stat = repository.get_statistics_slice()
    elif arguments.isdigit():
        day_filter: int = int(arguments)
        stat = repository.get_statistics_slice(day_filter)
    else:
        try:
            date_filter: datetime = datetime.strptime(arguments, "%d.%m.%Y").replace(tzinfo=pytz.UTC)
        except:
            await message.reply("Пожалуйста, введите дату в формате день.месяц.год. Например: 23.02.2022")
            return

        date_stat = repository.get_statistics(date_filter)
        if date_stat is None:
            await message.reply("За данное число не найдено статистики.")
            return
        else:
            stat = [date_stat]

    agg_stat: Dict[datetime, dict] = aggregate_events(stat)
    for day, day_stat in agg_stat.items():
        stat_messages = [
            f"Дата: {day.strftime('%d.%m.%Y')}",
            f"Уникальных пользователей: {day_stat.get('unique_users', 0)}",
            "Использованные команды:"
        ]
        for event, count in day_stat["events_count"].items():
            stat_messages.append(f"{event}: {count}")
        await message.answer("\n".join(stat_messages))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_statistics, commands=["stats"])
