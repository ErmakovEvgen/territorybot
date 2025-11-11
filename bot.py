import asyncio
import aiogram
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import asyncio, os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def start_command(message: Message):
    await message.answer("Привет, Junketsu! Бот работает 🚀")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.message.register(start_command, Command("start"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
