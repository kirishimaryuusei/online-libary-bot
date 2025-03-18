from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import SessionLocal
from database.models import Book
import html

router = Router()

cat_map = {
    "Художественная литература": "HL",
    "Нон-фикшен": "NF",
    "Детская литература": "DL",
    "Фэнтези": "F",
    "Детективы": "D",
    "Ужасы": "U",
    "Приключения": "P",
    "Фантастика": "FA",
    "Комиксы": "K",
    "Манга": "M",
    "Учебники": "UCH",
    "Психология": "PSY",
    "Научная литература": "NL",
    "Языковедение": "YAZ",
    "Биология": "BIO",
    "Общественные науки": "OSN",
    "Химия": "HIM",
    "Физика": "FIZ",
    "Математика": "MAT",
    "Книги для дошкольников": "KD",
    "Внеклассное чтение": "VC",
    "Книги для подростков": "KT"
}
reverse_cat_map = {v: k for k, v in cat_map.items()}

catalog_structure = {
    "Художественная литература": {
        "Фэнтези": {},
        "Детективы": {},
        "Ужасы": {},
        "Приключения": {},
        "Фантастика": {},
        "Комиксы": {},
        "Манга": {}
    },
    "Нон-фикшен": {
         "Учебники": {
             "Языковедение": {},
             "Биология": {},
             "Общественные науки": {},
             "Химия": {},
             "Физика": {},
             "Математика": {}
         },
         "Психология": {},
         "Научная литература": {}
    },
    "Детская литература": {
         "Книги для дошкольников": {},
         "Внеклассное чтение": {},
         "Книги для подростков": {}
    }
}

def get_current_level(path: list) -> dict:
    current = catalog_structure
    for p in path:
        current = current.get(p, {})
    return current

def build_catalog_keyboard(path: list) -> InlineKeyboardMarkup:
    current_level = get_current_level(path)
    keyboard = []
    if current_level:
        for option in current_level.keys():
            abbr = cat_map.get(option, option)
            new_path = path + [option]
            abbr_path = [cat_map.get(item, item) for item in new_path]
            callback_data = "catalog|" + "|".join(abbr_path)
            keyboard.append([InlineKeyboardButton(text=option, callback_data=callback_data)])
        nav_row = []
        if path:
            new_path = path[:-1]
            abbr_path = [cat_map.get(item, item) for item in new_path]
            callback_data = "catalog|" + "|".join(abbr_path) if new_path else "catalog|"
            nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data))
        nav_row.append(InlineKeyboardButton(text="Отмена ❌", callback_data="catalog_cancel"))
        keyboard.append(nav_row)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        return InlineKeyboardMarkup(inline_keyboard=[])

def build_books_keyboard(books: list) -> InlineKeyboardMarkup:
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

@router.callback_query(F.data == "catalog")
async def catalog_menu(callback: types.CallbackQuery):
    kb = build_catalog_keyboard([])
    await callback.message.answer("Выберите жанр 📚:", reply_markup=kb)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("catalog|"))
async def catalog_navigation(callback: types.CallbackQuery):
    data = callback.data.split("|")
    abbr_path = data[1:] if len(data) > 1 else []
    path_full = [reverse_cat_map.get(item, item) for item in abbr_path]
    current_level = get_current_level(path_full)
    if current_level:
        kb = build_catalog_keyboard(path_full)
        current_category = " > ".join(path_full)
        await callback.message.edit_text(f"Выберите жанр 📚: {current_category}", reply_markup=kb)
    else:
        genre = path_full[-1] if path_full else ""
        session = SessionLocal()
        books = session.query(Book).filter(Book.genre == genre).all()
        session.close()
        if books:
            text = f"Книги в категории «{html.escape(genre)}» 📚:\n"
            for i, book in enumerate(books):
                text += f"{i+1}. {book.author} - {book.title}\n"
            kb = build_books_keyboard(books)
            await callback.message.edit_text(text, reply_markup=kb)
        else:
            await callback.message.edit_text(f"В категории «{html.escape(genre)}» книг не найдено 😕.\nПополните базу командой /upload или выберите другую категорию.")
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("book_"))
async def select_catalog_book(callback: types.CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    session = SessionLocal()
    book = session.query(Book).filter_by(id=book_id).first()
    session.close()
    if book:
        await callback.message.answer_document(document=book.file_id, caption=f"{book.author} - {book.title} 📚")
    await callback.answer()

@router.callback_query(lambda c: c.data == "catalog_cancel")
async def catalog_cancel(callback: types.CallbackQuery):
    await callback.message.edit_text("Каталог отменен ❌")
    await callback.answer()
