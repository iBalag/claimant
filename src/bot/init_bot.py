from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


def init_bot(token: str) -> Dispatcher:
    storage: MemoryStorage = MemoryStorage()
    # storage: RedisStorage2 = RedisStorage2(host="localhost", port=6379, db=5, password=config["REDIS_PASSWORD"])

    bot: Bot = Bot(token=token)
    dp: Dispatcher = Dispatcher(bot, storage=storage)
    return dp
