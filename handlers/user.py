from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from database.database import SessionLocal
from database.models import Book
from keyboards.inline import books_keyboard
from aiogram.types import ReplyKeyboardRemove

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я LibraryBot 📚🤖. Используй команду /download для просмотра каталога, /upload для добавления книги и /lang для выбора языка. 😉", reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Доступные команды:\n/start – запуск бота 🚀\n/help – помощь 💡\n/download – просмотр каталога книг 📖\n/upload – загрузка книги 📥\n/lang – выбор языка 🌐", reply_markup=ReplyKeyboardRemove())

@router.message(Command("download"))
async def download_cmd(message: types.Message):
    session = SessionLocal()
    page = 0
    books = session.query(Book).limit(10).offset(page * 10).all()
    session.close()
    if not books:
        await message.answer("В каталоге пока нет книг 😕")
        return
    text = "Доступные книги:\n"
    for i, book in enumerate(books):
        text += f"{i+1}. {book.author} - {book.title}\n"
    kb = books_keyboard(page, len(books))
    await message.answer(text, reply_markup=kb)

@router.callback_query(lambda c: c.data == "download_cancel")
async def download_cancel(callback: types.CallbackQuery):
    await callback.message.edit_text("Просмотр каталога отменён. ❌")
    await callback.answer()

@router.callback_query(F.data.startswith("page_"))
async def paginate(callback: types.CallbackQuery):
    data = callback.data.split("_")
    page = int(data[1])
    direction = data[2]
    new_page = page - 1 if direction == "left" else page + 1
    session = SessionLocal()
    books = session.query(Book).limit(10).offset(new_page * 10).all()
    session.close()
    if not books:
        await callback.answer("Нет книг на этой странице 😕", show_alert=True)
        return
    text = "Доступные книги:\n"
    for i, book in enumerate(books):
        text += f"{i+1}. {book.author} - {book.title}\n"
    kb = books_keyboard(new_page, len(books))
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("book_"))
async def select_book(callback: types.CallbackQuery):
    _, page, index = callback.data.split("_")
    page = int(page)
    index = int(index) - 1
    session = SessionLocal()
    books = session.query(Book).limit(10).offset(page * 10).all()
    session.close()
    if index < len(books):
        book = books[index]
        await callback.message.answer_document(document=book.file_id, caption=f"{book.author} - {book.title} 📚")
    await callback.answer()
