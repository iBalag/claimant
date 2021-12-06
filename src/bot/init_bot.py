import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import dotenv_values

config = dotenv_values(".env")
logging.basicConfig(level=logging.INFO)

storage: MemoryStorage = MemoryStorage()

bot: Bot = Bot(token=config["API_TOKEN"])
dp: Dispatcher = Dispatcher(bot, storage=storage)
