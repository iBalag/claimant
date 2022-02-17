import argparse
import logging

from aiogram import executor, Dispatcher
from dotenv import dotenv_values

from handlers import start_menu, head_part_handler, story_part_handler, essence_part_handler, proofs_part_handler, \
    claims_part_handler, additions_part_handler, download_doc_handler, admin_actions_handler
from init_bot import init_bot
import bot_config


logging.basicConfig(level=logging.INFO)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--environment", type=str, help="Environment name: dev or prod.", choices=["dev", "prod"])
    args = parser.parse_args()
    bot_config.ENV = args.environment
    if bot_config.ENV == "prod":
        config = dotenv_values(".env")
    elif bot_config.ENV == "dev":
        config = dotenv_values(".env-dev")
    else:
        raise EnvironmentError("Provided environment name is not allowed.")

    dp = init_bot(config["API_TOKEN"])

    start_menu.register_handlers(dp)
    head_part_handler.register_handlers(dp)
    story_part_handler.register_handlers(dp)
    essence_part_handler.register_handlers(dp)
    proofs_part_handler.register_handlers(dp)
    claims_part_handler.register_handlers(dp)
    additions_part_handler.register_handlers(dp)
    download_doc_handler.register_handlers(dp)
    admin_actions_handler.register_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
