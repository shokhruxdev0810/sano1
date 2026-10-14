import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject

import config
from database.db import init_db, AsyncSessionLocal
from data.seed import seed_data
from handlers import main_router

# Logging (Railway loglarida ko'rinishi uchun stdout'ga)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    """Har bir update uchun async SQLAlchemy sessiyasini handlerga uzatadi."""
    async def __call__(self, handler, event: TelegramObject, data: dict):
        async with AsyncSessionLocal() as session:
            data["session"] = session
            return await handler(event, data)


async def main() -> int:
    """Botni ishga tushiradi. 0 = normal to'xtash, 1 = xatolik (Railway qayta ishga tushiradi)."""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN sozlanmagan! Railway: Service -> Variables ga BOT_TOKEN qo'shing (lokal: .env faylga).")
        return 1

    if config.STORAGE_WARNING:
        logger.warning(config.STORAGE_WARNING)
    if config.SQLITE_PATH:
        logger.info(f"Baza fayli: {config.SQLITE_PATH}")
    if not config.ADMIN_IDS:
        logger.warning("ADMIN_ID sozlanmagan — admin panel va buyurtma xabarlari ishlamaydi.")

    logger.info("Initializing database...")
    await init_db()

    # MUHIM: faqat baza bo'sh bo'lganda demo ma'lumot yoziladi. Mavjud ma'lumotlar hech qachon o'chirilmaydi.
    logger.info("Seeding initial data if database is empty...")
    try:
        await seed_data(force_reseed=False)
    except Exception as e:
        logger.warning(f"Seed data error: {e}")

    try:
        bot = Bot(token=config.BOT_TOKEN)
    except Exception as e:
        logger.error(f"BOT_TOKEN noto'g'ri formatda: {e}")
        return 1

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(main_router)

    logger.info("SANO BOOKS Telegram Bot started!")
    logger.info(f"Admin IDs: {config.ADMIN_IDS}")

    exit_code = 0
    try:
        # Webhookni o'chirib, polling boshlaymiz
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Bot crash error: {e}", exc_info=True)
        exit_code = 1  # nolga teng bo'lmagan kod -> Railway avtomatik qayta ishga tushiradi
    finally:
        await bot.session.close()
    return exit_code


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
        code = 0
    sys.exit(code)
