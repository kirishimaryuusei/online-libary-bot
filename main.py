import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import TOKEN
from database.database import init_db
from handlers import user, admin, books, search, catalog

async def main():
    init_db()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(books.router)
    dp.include_router(search.router)
    dp.include_router(catalog.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
