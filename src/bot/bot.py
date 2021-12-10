from aiogram import executor

from handlers import start_menu, court_resolver
from init_bot import dp


if __name__ == "__main__":
    start_menu.register_handlers(dp)
    court_resolver.register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
