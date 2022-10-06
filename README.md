# Sitescreenshot_bot

Telegram bot responds to any link in the chat and offers the user a screenshot of the site.
____

## Installation

1. `git clone https://github.com/yoninjago/sitescreenshot_bot.git`
2. `cd` into new directory
3. Copy `.env.example` to your `.env` file
4. Fill `.env` file with your credentials

## Usage
Run `docker-compose up -d` to start.
____

## Used tech:
- Python 3.10+
- [aiogram](https://github.com/aiogram/aiogram)
- [SQLAlchemy 1.4+](https://www.sqlalchemy.org/)
- [Pyppeteer](https://github.com/pyppeteer/pyppeteer)
- PostgreSQL as database
- asyncpg as database driver for SQLAlchemy
- Docker with docker-compose for deployment