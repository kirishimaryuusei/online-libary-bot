from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def remove_keyboard():
    return ReplyKeyboardRemove()

def main_menu_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Каталог книг"), KeyboardButton(text="Загрузить книгу")]
    ], resize_keyboard=True)
