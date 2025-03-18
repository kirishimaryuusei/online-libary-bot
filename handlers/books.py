from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import SessionLocal
from database.models import Book

router = Router()

class UploadBook(StatesGroup):
    waiting_for_file = State()
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_genre = State()

@router.message(Command("upload"))
async def upload_book(message: types.Message, state: FSMContext):
    await message.answer("Пришлите файл книги (PDF, EPUB, FB2).")
    await state.set_state(UploadBook.waiting_for_file)

@router.message(UploadBook.waiting_for_file, F.document)
async def process_file(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    await state.update_data(file_id=file_id)
    await message.answer("Введите название книги.")
    await state.set_state(UploadBook.waiting_for_title)

@router.message(UploadBook.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите автора книги (заглавными буквами).")
    await state.set_state(UploadBook.waiting_for_author)

@router.message(UploadBook.waiting_for_author)
async def process_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.answer("Введите жанр книги.")
    await state.set_state(UploadBook.waiting_for_genre)

@router.message(UploadBook.waiting_for_genre)
async def process_genre(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = SessionLocal()
    existing = db.query(Book).filter_by(title=data["title"], author=data["author"], language="russian").first()
    if existing:
        await message.answer("Такая книга уже существует в каталоге.")
    else:
        new_book = Book(title=data["title"], author=data["author"], genre=data["genre"], file_id=data["file_id"], language="russian")
        db.add(new_book)
        db.commit()
        await message.answer("Книга успешно добавлена!")
    db.close()
    await state.clear()
