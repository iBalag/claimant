import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from dotenv import dotenv_values

config = dotenv_values(".env")
logging.basicConfig(level=logging.INFO)

storage: MemoryStorage = MemoryStorage()
# storage: RedisStorage2 = RedisStorage2(host="localhost", port=6379, db=5, password=config["REDIS_PASSWORD"])

bot: Bot = Bot(token=config["API_TOKEN"])
dp: Dispatcher = Dispatcher(bot, storage=storage)
