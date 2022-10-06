import re
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, Sequence

from emoji import emojize
from pyppeteer import errors, launch

from .exceptions import ScreenshotError

SCREENSHOTS_PATH = Path(__file__).parents[1].joinpath('screenshots')
CHROMIUM_PATH = '/usr/bin/google-chrome-stable'
IMAGE_NAME = '{date}_{user_id}_{domain}.png'
PAGE_NOT_FOUND = emojize(
    ':recycle: <b>Страница не найдена.</b>', language='alias'
)
PAGE_TIMEOUT = emojize(
    ':hourglass: <b>Превышено время ожидания ответа</b>', language='alias'
)


def time_of_function(func: Callable) -> Callable:
    """
    Simple decorator to measure the execution time of func.
    Unpacked return of func, execution time in seconds.
    """
    @wraps(func)
    async def wraper(*args, **kwargs) -> tuple[Sequence, int]:
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        execution_time = round(time.perf_counter() - start_time)
        return *result, execution_time
    return wraper


def check_url(url: str) -> str:
    """
    Verifies if given link has http or https URI scheme. If not sets https.
    """
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    return url


def get_domain(url: str) -> str:
    """
    Returns domain from URL
    """
    return re.split(r'http.?:\/\/([\da-z\.-]+\.[a-z\.]{2,6})*\/?', url)[1]


def get_image_name(url: str, user_id: int) -> str:
    """
    Generates a file name from the current date, user_id and domain.
    """
    return IMAGE_NAME.format(
        date=datetime.now().date(),
        user_id=str(user_id),
        domain=get_domain(url))


@time_of_function
async def get_screenshot(
        url: str, user_id: int) -> tuple[bytes | str, str, str]:
    """
    Takes screenshot of given URL and saves it to SCREENSHOTS_PATH dir.
    """
    url = check_url(url)
    browser = await launch(
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
            ],
            headless=True,
            ignoreHTTPSErrors=True,
            executablePath=CHROMIUM_PATH,
            handleSIGINT=False,)

    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 1280})

    try:
        await page.goto(url, {'timeout': 35000})
    except errors.PageError:
        raise ScreenshotError(PAGE_NOT_FOUND)
    except errors.TimeoutError:
        raise ScreenshotError(PAGE_TIMEOUT)

    screenshot = await page.screenshot(
        {'path': SCREENSHOTS_PATH / get_image_name(url, user_id)}
        )
    page_title = await page.title()
    await browser.close()

    return screenshot, page_title, url
