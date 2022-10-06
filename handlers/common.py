import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters
from aiogram.utils import deep_linking
from emoji import emojize

from db.models import Statistics, User
from handlers.db import get_or_create
from utils.exceptions import ScreenshotError, WHOISError
from utils.get_screenshot import get_domain, get_screenshot
from utils.whois import parse_whois


START_MESSAGE = emojize(
    ':wave: Привет! Меня зовут <b>ScreenShotBot</b>.\n'
    'Я - Бот для создания веб-скриншотов.\n'
    'Чтобы получить скриншот - отправьте URL адрес сайта.'
    ' Например, ya.ru\n\n'
    '• С помощью бота вы можете проверять подозрительные ссылки.'
    ' <i>(Айпилоггеры, фишинговые веб-сайты, скримеры и т.п)</i>.\n'
    '• Вы также можете добавить меня в свои чаты, и я смогу проверять ссылки,'
    ' которые отправляют пользователи.', language='alias'
)
ADD_BOT_TO_CHAT = emojize(':paperclip: Добавить бота в ваш чат')
FOUND_LINK_MESSAGE = '<b>В сообщении найдена ссылка!</b>\n'
SCREENSHOT_DESCRIPTION = (
    '{title}\n\n<b>Веб-сайт:</b> {domain}\n'
    '<b>Время обработки:</b> {duration} секунд'
)
REQUEST_SEND = emojize(
    '<b>:satellite: Запрос отправлен на сайт.</b>', language='alias'
)
SUCCESS_REQUEST = 'Успешный запрос к {domain}'
SUCCESS_WHOIS = 'Успешный запрос WHOIS для {domain}'
ERROR = emojize(
    ':warning: Произошла ошибка. Попробуйте сделать запрос позже',
    language='alias'
)
DETAIL = emojize(':mag_right: Подробнее', language='alias')


logger = logging.getLogger(__name__)


async def start(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text=ADD_BOT_TO_CHAT,
        url=await deep_linking.get_startgroup_link('true')
        )
    )
    await message.answer(START_MESSAGE, reply_markup=keyboard)


async def search_url(message: types.Message):
    """
    Search for URLs in user messages.
    """
    for entity in message.entities:
        if entity.type in ('url', 'text_link'):
            url_offset = f'{entity.offset} {entity.offset + entity.length}'
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=DETAIL, callback_data=f'get_screen_from_{url_offset}')
            )
            await message.reply(FOUND_LINK_MESSAGE, reply_markup=keyboard)


async def get_screen_from_url(call: types.CallbackQuery):
    """
    Handler for getting website's screenshot.
    """
    await call.message.edit_text(REQUEST_SEND)
    url_offset = [
        int(num) for num in call.data[len('get_screen_from_')::].split(' ')
    ]
    url = call.message.reply_to_message.text[url_offset[0]:url_offset[1]]
    db_session = call.bot.get('db')
    user = await get_or_create(db_session, User, tg_id=call.from_user.id)
    new_stat = Statistics(user_id=user.id, url=url, success=False)

    try:
        image, page_title, domain, duration = await get_screenshot(
            url=url,
            user_id=call.from_user.id
        )
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=DETAIL, callback_data=f'get_whois_{get_domain(domain)}')
        )
        await call.message.delete()
        await call.message.answer_photo(
            image,
            SCREENSHOT_DESCRIPTION.format(
                title=page_title, domain=domain, duration=duration),
            reply_markup=keyboard
        )
        logger.info(SUCCESS_REQUEST.format(domain=domain))
        new_stat.success = True

    except ScreenshotError as error:
        logger.exception(error)
        await call.message.edit_text(error.args[0])

    except Exception as error:
        logger.exception(error)
        await call.message.edit_text(ERROR)

    finally:
        async with db_session() as session:
            session.add(new_stat)
            await session.commit()


async def get_whois(call: types.CallbackQuery):
    """
    Handler for getting whois.
    """
    text = ERROR
    domain = call.data[len('get_whois_')::]
    try:
        text = await parse_whois(domain)
        logger.info(SUCCESS_WHOIS.format(domain=domain))
    except WHOISError as error:
        logger.exception(error)
    except Exception as error:
        logger.exception(error)
    await call.answer(text=text, show_alert=True)


def register_handlers_common(dispatcher: Dispatcher):
    """
    Handlers registration.
    """
    dispatcher.register_message_handler(
        start, filters.CommandStart()
    )
    dispatcher.register_message_handler(search_url)
    dispatcher.register_callback_query_handler(
        get_screen_from_url, filters.Text(startswith='get_screen_from_')
    )
    dispatcher.register_callback_query_handler(
        get_whois, filters.Text(startswith='get_whois_')
    )
