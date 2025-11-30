from typing import cast

from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from aiogram.fsm.context import FSMContext

from bot import dp, conn
from states import (
    MovieForm,
    MovieData,
    AddAdminForm,
    DeleteAdminForm,
    DeleteMovieForm,
)
from utils import is_integer


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"👋 Salom, {message.from_user.first_name}! Botga xush kelibsiz."
    )


@dp.message(Command("addmovie"))
async def addmovie_handler(message: Message, state: FSMContext):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins;")
    admins = cursor.fetchall()
    user_id = message.from_user.id

    is_user_admin = any(admin[1] == user_id for admin in admins)
    
    if is_user_admin:
        await message.answer("🎬 Iltimos, kino nomini yuboring.")
        await state.set_state(MovieForm.title)
    else:
        await message.answer("🚫 Kechirasiz, siz admin emassiz.")


@dp.message(MovieForm.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📅 Kino yilini kiriting.")
    await state.set_state(MovieForm.year)


@dp.message(MovieForm.year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=int(message.text))
    await message.answer("⏱️ Kino davomiyligini (daqiqada) kiriting.")
    await state.set_state(MovieForm.duration)


@dp.message(MovieForm.duration)
async def get_duration(message: Message, state: FSMContext):
    await state.update_data(duration=int(message.text))
    await message.answer("🎭 Kino janrini kiriting.")
    await state.set_state(MovieForm.genre)


@dp.message(MovieForm.genre)
async def get_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("⭐ Kino reytingini kiriting (masalan: 8.5).")
    await state.set_state(MovieForm.rating)


@dp.message(MovieForm.rating)
async def get_rating(message: Message, state: FSMContext):
    await state.update_data(rating=float(message.text))
    await message.answer("🗣️ Kino tilini kiriting.")
    await state.set_state(MovieForm.language)


@dp.message(MovieForm.language)
async def get_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer("📹 Kino videosini yuboring.")
    await state.set_state(MovieForm.video)


@dp.message(MovieForm.video, F.video)
async def get_video(message: Message, state: FSMContext):
    await state.update_data(file_id=message.video.file_id)
    data = cast(MovieData, await state.get_data())

    caption = (
        "📋 Ma'lumotlarni tasdiqlang:\n"
        f"🎬 Nomi: {data['title']}\n"
        f"📅 Yili: {data['year']}\n"
        f"⏱️ Davomiyligi: {data['duration']} daqiqa\n"
        f"🎭 Janri: {data['genre']}\n"
        f"⭐ Reyting: {data['rating']}\n"
        f"🗣️ Tili: {data['language']}"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❌ Bekor qilish"),
                KeyboardButton(text="✅ Tasdiqlash"),
            ]
        ],
        resize_keyboard=True,
    )

    await message.answer_video(data["file_id"], caption=caption, reply_markup=keyboard)
    await state.set_state(MovieForm.confirm)


@dp.message(MovieForm.confirm)
async def get_confirm(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "🚫 Ma'lumotlar bekor qilindi.", reply_markup=ReplyKeyboardRemove()
        )
    elif message.text == "✅ Tasdiqlash":
        data = cast(MovieData, await state.get_data())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO movies (title, year, duration, genre, rating, language, file_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                data["title"],
                data["year"],
                data["duration"],
                data["genre"],
                data["rating"],
                data["language"],
                data["file_id"],
            ),
        )
        conn.commit()
        await message.answer(
            f"✅ Ma'lumotlar saqlandi.\n🎬 Kino kodi: {cursor.lastrowid}",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()


@dp.message(Command("addadmin"))
async def add_admin_handler(message: Message, state: FSMContext):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins;")
    admins = cursor.fetchall()
    user_id = message.from_user.id

    is_user_admin = any(admin[1] == user_id for admin in admins)

    if is_user_admin:
        await message.answer(
            "🆔 Yangi adminning Telegram ID sini kiriting (faqat raqam)."
        )
        await state.set_state(AddAdminForm.telegram_id)
    else:
        await message.answer("🚫 Siz admin emassiz.")


@dp.message(AddAdminForm.telegram_id)
async def get_admin_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("🚫 ID faqat raqamlardan iborat bo‘lishi kerak.")
        return
    if len(message.text) < 10:
        await message.answer("🚫 ID noto‘g‘ri. Kamida 10 ta raqam bo‘lishi kerak.")
        return

    await state.update_data(telegram_id=int(message.text))
    await message.answer("👤 Adminning ismini kiriting.")
    await state.set_state(AddAdminForm.first_name)


@dp.message(AddAdminForm.first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("👥 Familiyani kiriting (ixtiyoriy, bo‘sh qoldirish mumkin).")
    await state.set_state(AddAdminForm.last_name)


@dp.message(AddAdminForm.last_name)
async def get_last_name(message: Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(last_name=message.text)
    await message.answer(
        "🔤 Telegram username ni kiriting (ixtiyoriy, bo‘sh qoldirish mumkin)."
    )
    await state.set_state(AddAdminForm.username)


@dp.message(AddAdminForm.username)
async def get_username(message: Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(username=message.text)
    else:
        await state.update_data(username=None)

    data = await state.get_data()
    caption = (
        "📋 Yangi admin ma'lumotlari:\n"
        f"🆔 ID: {data['telegram_id']}\n"
        f"👤 Ism: {data['first_name']}\n"
        f"👥 Familiya: {data['last_name'] or '—'}\n"
        f"🔤 Username: {data['username'] or '—'}\n\n"
        "✅ Tasdiqlaysizmi?"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Bekor qilish"),
            ]
        ],
        resize_keyboard=True,
    )

    await message.answer(caption, reply_markup=keyboard)
    await state.set_state(AddAdminForm.confirm)


@dp.message(AddAdminForm.confirm)
async def confirm_admin(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "🚫 Ma'lumotlar bekor qilindi.", reply_markup=ReplyKeyboardRemove()
        )
    elif message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admins (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?);",
            (
                data["telegram_id"],
                data["first_name"],
                data["last_name"],
                data["username"],
            ),
        )
        conn.commit()
        await state.clear()
        await message.answer(
            "✅ Yangi admin muvaffaqiyatli qo‘shildi!",
            reply_markup=ReplyKeyboardRemove(),
        )


@dp.message(Command("deleteadmin"))
async def delete_admin_handler(message: Message, state: FSMContext):
    super_admin_id = 6296302270

    if message.from_user.id != super_admin_id:
        await message.answer("🚫 Sizda adminlarni o‘chirish huquqi yo‘q.")
        return

    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, first_name FROM admins WHERE user_id != ?;", (super_admin_id,)
    )
    admins = cursor.fetchall()

    if not admins:
        await message.answer("ℹ️ O‘chiriladigan boshqa adminlar yo‘q.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=admin[1])] for admin in admins],
        resize_keyboard=True,
    )

    await state.update_data(admins=admins)
    await message.answer("👥 O‘chiriladigan adminni tanlang:", reply_markup=keyboard)
    await state.set_state(DeleteAdminForm.choose_admin)


@dp.message(DeleteAdminForm.choose_admin)
async def choose_admin_to_delete(message: Message, state: FSMContext):
    data = await state.get_data()
    admins = data["admins"]

    selected_name = message.text
    selected_admin = next(
        (admin for admin in admins if admin[1] == selected_name), None
    )

    if not selected_admin:
        await message.answer("🚫 Bunday admin topilmadi.")
        return

    await state.update_data(
        selected_admin_id=selected_admin[0], selected_admin_name=selected_name
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Bekor qilish"),
            ]
        ],
        resize_keyboard=True,
    )

    await message.answer(
        f"🗑️ {selected_name} adminini o‘chirmoqchimisiz?", reply_markup=keyboard
    )
    await state.set_state(DeleteAdminForm.confirm)


@dp.message(DeleteAdminForm.confirm)
async def confirm_admin_deletion(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "🚫 O‘chirish bekor qilindi.", reply_markup=ReplyKeyboardRemove()
        )
        return

    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        admin_id = data["selected_admin_id"]
        admin_name = data["selected_admin_name"]

        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE user_id = ?;", (admin_id,))
        conn.commit()

        await state.clear()
        await message.answer(
            f"✅ {admin_name} admini o‘chirildi.", reply_markup=ReplyKeyboardRemove()
        )


@dp.message(Command("deletemovie"))
async def delete_movie_handler(message: Message, state: FSMContext):
    super_admin_id = 6296302270

    if message.from_user.id != super_admin_id:
        await message.answer("🚫 Sizda kinolarni o‘chirish huquqi yo‘q.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM movies;")
    movies = cursor.fetchall()

    if not movies:
        await message.answer("ℹ️ O‘chiriladigan kinolar topilmadi.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=movie[1])] for movie in movies],
        resize_keyboard=True,
    )

    await state.update_data(movies=movies)
    await message.answer("🎬 O‘chiriladigan kinoni tanlang:", reply_markup=keyboard)
    await state.set_state(DeleteMovieForm.choose_movie)


@dp.message(DeleteMovieForm.choose_movie)
async def choose_movie_to_delete(message: Message, state: FSMContext):
    data = await state.get_data()
    movies = data["movies"]

    selected_title = message.text
    selected_movie = next(
        (movie for movie in movies if movie[1] == selected_title), None
    )

    if not selected_movie:
        await message.answer("🚫 Bunday kino topilmadi.")
        return

    await state.update_data(
        selected_movie_id=selected_movie[0], selected_movie_title=selected_title
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Bekor qilish"),
            ]
        ],
        resize_keyboard=True,
    )

    await message.answer(
        f'🗑️ "{selected_title}" kinoni o‘chirmoqchimisiz?', reply_markup=keyboard
    )
    await state.set_state(DeleteMovieForm.confirm)


@dp.message(DeleteMovieForm.confirm)
async def confirm_movie_deletion(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "🚫 O‘chirish bekor qilindi.", reply_markup=ReplyKeyboardRemove()
        )
        return

    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        movie_id = data["selected_movie_id"]
        movie_title = data["selected_movie_title"]

        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?;", (movie_id,))
        conn.commit()

        await state.clear()
        await message.answer(
            f'✅ "{movie_title}" kinoni muvaffaqiyatli o‘chirildi.',
            reply_markup=ReplyKeyboardRemove(),
        )


@dp.message()
async def get_id(message: Message):
    if is_integer(message.text):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE id = ?;", (int(message.text),))
        movie = cursor.fetchone()
        if movie:
            caption = (
                f"🎬 Nomi: {movie[1]}\n"
                f"📅 Yili: {movie[2]}\n"
                f"⏱️ Davomiyligi: {movie[3]} daqiqa\n"
                f"🎭 Janri: {movie[4]}\n"
                f"⭐ Reyting: {movie[5]}\n"
                f"🗣️ Tili: {movie[6]}"
            )
            await message.answer_video(movie[7], caption=caption)
        else:
            await message.answer("🚫 Noto‘g‘ri kino kodi kiritildi!")
    else:
        await message.answer("🚫 Iltimos, faqat raqamli kino kodini kiriting!")
