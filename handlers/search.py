from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import SessionLocal
from database.models import Book, User
import html

router = Router()

class SearchBook(StatesGroup):
    waiting_for_query = State()

def search_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Поиск по автору", callback_data="search_author")],
        [InlineKeyboardButton(text="📖 Поиск по названию", callback_data="search_title")]
    ])

def search_results_keyboard(books: list) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for i, book in enumerate(books):
        row.append(InlineKeyboardButton(text=str(i+1), callback_data=f"book_{book.id}"))
        if (i+1) % 5 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "search")
async def search_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите тип поиска 🔍:", reply_markup=search_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data.in_(["search_author", "search_title"]))
async def set_search_type(callback: types.CallbackQuery, state: FSMContext):
    search_type = callback.data.split("_")[1]
    await state.update_data(search_type=search_type)
    prompt = "Напишите имя или псевдоним автора книги 📚🔎:" if search_type == "author" else "Напишите название книги 📖🔎:"
    await callback.message.answer(prompt, reply_markup=ReplyKeyboardRemove())
    await state.set_state(SearchBook.waiting_for_query)
    await callback.answer()

@router.message(SearchBook.waiting_for_query)
async def process_search_query(message: types.Message, state: FSMContext):
    query = message.text.strip()
    data = await state.get_data()
    search_type = data.get("search_type")
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=message.from_user.id).first()
    lang = user.language if user else "russian"
    if search_type == "author":
        books = db.query(Book).filter(Book.author.ilike(f"%{query}%"), Book.language==lang).all()
        alt = "по названию"
    elif search_type == "title":
        books = db.query(Book).filter(Book.title.ilike(f"%{query}%"), Book.language==lang).all()
        alt = "по автору"
    else:
        books = []
        alt = ""
    db.close()
    if books:
        text = "Найденные книги 📚:\n"
        for i, book in enumerate(books):
            text += f"{i+1}. {book.author} - {book.title}\n"
        kb = search_results_keyboard(books)
        await message.answer(text, reply_markup=kb)
    else:
        await message.answer(f"Ни одной книги по запросу «{html.escape(query)}» не найдено 😕.\nВы можете пополнить базу командой /upload или попробовать поиск {alt}.")
    await state.clear()

@router.callback_query(F.data.startswith("book_"))
async def select_search_book(callback: types.CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    db = SessionLocal()
    book = db.query(Book).filter_by(id=book_id).first()
    db.close()
    if book:
        await callback.message.answer_document(document=book.file_id, caption=f"{book.author} - {book.title} 📚")
    await callback.answer()
