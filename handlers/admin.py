from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import SessionLocal
from database.models import Book
from config import ADMIN_IDS

router = Router()

class AdminUploadBook(StatesGroup):
    waiting_for_file = State()
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_genre = State()
    waiting_for_language = State()

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен.")
        return
    await message.answer("Добро пожаловать в админ-панель.", reply_markup=admin_keyboard())

def admin_keyboard():
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Добавить книгу", callback_data="admin_add_book")],
        [types.InlineKeyboardButton(text="Список книг", callback_data="admin_list_books")],
        [types.InlineKeyboardButton(text="Удалить книгу", callback_data="admin_delete_book")]
    ])
    return keyboard

@router.callback_query(F.data=="admin_add_book")
async def admin_add_book(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен.")
        return
    await callback.message.edit_text("Пришлите файл книги (PDF, EPUB, FB2) для добавления:")
    await state.set_state(AdminUploadBook.waiting_for_file)
    await callback.answer()

@router.message(AdminUploadBook.waiting_for_file, F.document)
async def admin_process_file(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен.")
        return
    file_id = message.document.file_id
    await state.update_data(file_id=file_id)
    await message.answer("Введите название книги:")
    await state.set_state(AdminUploadBook.waiting_for_title)

@router.message(AdminUploadBook.waiting_for_title)
async def admin_process_title(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен.")
        return
    await state.update_data(title=message.text)
    await message.answer("Введите автора книги (заглавными буквами):")
    await state.set_state(AdminUploadBook.waiting_for_author)

@router.message(AdminUploadBook.waiting_for_author)
async def admin_process_author(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен.")
        return
    await state.update_data(author=message.text)
    await message.answer("Введите жанр книги:")
    await state.set_state(AdminUploadBook.waiting_for_genre)

@router.message(AdminUploadBook.waiting_for_genre)
async def admin_process_genre(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен.")
        return
    await state.update_data(genre=message.text)
    await message.answer("Введите язык книги (russian/english):")
    await state.set_state(AdminUploadBook.waiting_for_language)

@router.message(AdminUploadBook.waiting_for_language)
async def admin_process_language(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Доступ запрещен.")
        return
    lang = message.text.lower()
    if lang not in ["russian", "english"]:
        await message.answer("Пожалуйста, введите 'russian' или 'english'.")
        return
    await state.update_data(language=lang)
    data = await state.get_data()
    db = SessionLocal()
    existing = db.query(Book).filter_by(title=data["title"], author=data["author"], language=lang).first()
    if existing:
        await message.answer("Такая книга уже существует в каталоге.")
    else:
        new_book = Book(title=data["title"], author=data["author"], genre=data["genre"], file_id=data["file_id"], language=lang)
        db.add(new_book)
        db.commit()
        await message.answer("Книга успешно добавлена!")
    db.close()
    await state.clear()
