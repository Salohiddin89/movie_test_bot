import os
import dotenv
import sqlite3

from aiogram import Bot, Dispatcher
from create_tables import create_tables

dotenv.load_dotenv()
create_tables()

conn = sqlite3.connect("movies.db")

bot = Bot(str(os.getenv("BOT_TOKEN")))
dp = Dispatcher()
