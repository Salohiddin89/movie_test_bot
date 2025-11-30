import asyncio
from aiogram.types.bot_command import BotCommand

from keep_alive import keep_alive
from bot import dp, bot
import handlers  # noqa: F401 (registers handlers by import)


def on_start():
    print("✅ Bot ishga tushdi...")


async def main():
    dp.startup.register(on_start)
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="addmovie", description="Kino qo‘shish"),
            BotCommand(command="addadmin", description="Admin qo‘shish"),
            BotCommand(command="deleteadmin", description="Admini ochirish"),
            BotCommand(command="deletemovie", description="Movie ni ochirish"),
        ]
    )
    await dp.start_polling(bot)


# Original behavior preserved:
asyncio.run(main())

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
