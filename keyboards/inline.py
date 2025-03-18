from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def books_keyboard(page: int, books_count: int) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for i in range(books_count):
        row.append(InlineKeyboardButton(text=str(i+1), callback_data=f"book_{page}_{i+1}"))
        if (i+1) % 5 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    nav_row = []
    if page == 0:
        nav_row.append(InlineKeyboardButton(text="Отмена ❌", callback_data="download_cancel"))
    else:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page}_left"))
    nav_row.append(InlineKeyboardButton(text="🔍 Поиск", callback_data="search"))
    nav_row.append(InlineKeyboardButton(text="📚 Каталог", callback_data="catalog"))
    nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{page}_right"))
    keyboard.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
