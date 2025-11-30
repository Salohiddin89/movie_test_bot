from aiogram.fsm.state import StatesGroup, State
from typing import TypedDict


class MovieForm(StatesGroup):
    title = State()
    year = State()
    duration = State()
    genre = State()
    rating = State()
    language = State()
    video = State()
    confirm = State()


class MovieData(TypedDict):
    title: str
    year: int
    duration: int
    genre: str
    rating: float
    language: str
    file_id: str


class DeleteAdminForm(StatesGroup):
    choose_admin = State()
    confirm = State()


class AddAdminForm(StatesGroup):
    telegram_id = State()
    first_name = State()
    last_name = State()
    username = State()
    confirm = State()


class DeleteMovieForm(StatesGroup):
    choose_movie = State()
    confirm = State()
