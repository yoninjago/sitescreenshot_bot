import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types

from config.loader import config
from db.base import async_session, init_models
from handlers.common import register_handlers_common
from utils.set_bot_commands import set_default_commands


LOG_FILENAME = __file__.split('/')[-1] + '.log'
LOG_PATH = Path(__file__).parents[0] / 'logs' / LOG_FILENAME

logger = logging.getLogger(__name__)


async def on_startup(dispatcher: Dispatcher):
    register_handlers_common(dispatcher)
    await set_default_commands(dispatcher)
    await init_models()


def main():
    formatter = logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s] Event: %(message)s'
    )
    file_handler = RotatingFileHandler(
        LOG_PATH, maxBytes=1000000, backupCount=2
    )
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=(file_handler,))

    bot = Bot(token=config.tg_bot.token, parse_mode=types.ParseMode.HTML)
    bot["db"] = async_session
    dispatcher = Dispatcher(bot)

    try:
        executor.start_polling(
            dispatcher,
            skip_updates=True,
            on_startup=on_startup
        )
    except Exception as error:
        logger.exception(error)


if __name__ == '__main__':
    main()
