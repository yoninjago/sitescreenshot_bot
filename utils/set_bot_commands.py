from aiogram import Dispatcher, types


async def set_default_commands(dispatcher: Dispatcher):
    """
    Sets default bot commands.
    """
    await dispatcher.bot.set_my_commands(
        [
            types.BotCommand("start", description="About ScreenShotBot"),
        ]
    )
