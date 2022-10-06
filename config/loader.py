import logging
import os
from dataclasses import asdict, dataclass
from typing import ClassVar

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_ENGINE = os.getenv('DB_ENGINE')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

ENVIRONMENT_VARIABLES_MISSING = (
    'Отсутствуют обязательные переменные окружения: {name}')
TOKENS_NAMES = (
    'BOT_TOKEN', 'DB_ENGINE', 'DB_HOST',
    'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'
)
STOP_BOT = 'Программа принудительно остановлена.'


@dataclass
class TgBot:
    token: str


@dataclass
class DBConfig:
    engine: str
    host: str
    port: int
    database: str
    user: str
    password: str
    DATABASE_URL: ClassVar[str] = (
        '{engine}://{user}:{password}@{host}:{port}/{database}')

    @property
    def url(self):
        """Create database connection URL"""
        return self.DATABASE_URL.format(**asdict(self))


@dataclass
class Config:
    tg_bot: TgBot
    db: DBConfig


def check_environments() -> bool:
    """Checking environment for the existence of a variable."""
    missing_tokens = [name for name in TOKENS_NAMES if not globals()[name]]
    if missing_tokens:
        logger.critical(ENVIRONMENT_VARIABLES_MISSING.format(
            name=','.join(missing_tokens))
        )
        return False
    return True


def load_config() -> Config:
    """Loading bot token and database connection details."""
    if not check_environments():
        raise ValueError(STOP_BOT)
    return Config(
        tg_bot=TgBot(token=BOT_TOKEN),
        db=DBConfig(
            engine=DB_ENGINE,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    )


config: Config = load_config()
