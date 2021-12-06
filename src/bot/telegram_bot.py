import logging

from aiogram import Bot, Dispatcher, executor, types
from dotenv import dotenv_values

from init_bot import dp
from handlers import start_menu


if __name__ == '__main__':
    start_menu.register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
