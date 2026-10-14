import os
import shutil
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# .env faylini yuklash (lokal ishlatish uchun; Railway'da Variables ishlatiladi)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PREFIX = "sqlite+aiosqlite:///"


def _clean(value: Optional[str]) -> str:
    """Railway Variables'ga paste qilinganda tasodifan tushib qolgan bo'sh joy/qo'shtirnoqlarni olib tashlaydi."""
    return (value or "").strip().strip('"').strip("'").strip()


BOT_TOKEN: str = _clean(os.getenv("BOT_TOKEN"))

# ADMIN_IDS yoki ADMIN_ID (vergul bilan ajratilgan Telegram ID ro'yxati)
ADMIN_IDS_RAW: str = _clean(os.getenv("ADMIN_IDS")) or _clean(os.getenv("ADMIN_ID"))
ADMIN_IDS: list[int] = [
    int(i.strip())
    for i in ADMIN_IDS_RAW.split(",")
    if i.strip().isdigit() and int(i.strip()) > 0
]

# Railway muhiti aniqlash
VOLUME_PATH: str = _clean(os.getenv("RAILWAY_VOLUME_MOUNT_PATH"))
ON_RAILWAY: bool = bool(
    os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID") or VOLUME_PATH
)

SQLITE_PATH: Optional[Path] = None
STORAGE_WARNING: Optional[str] = None


def _resolve_database_url() -> str:
    """DATABASE_URL ni to'g'ri va xavfsiz ko'rinishga keltiradi.

    - Bo'sh bo'lsa: Railway Volume bor bo'lsa -> <volume>/sano_books.db, aks holda lokal ./sano_books.db
    - 'sqlite:///' -> 'sqlite+aiosqlite:///' ga o'giriladi
    - Nisbiy (relative) SQLite yo'li + Railway Volume bo'lsa -> baza Volume ichiga ko'chiriladi,
      aks holda har deployda ma'lumotlar o'chib ketar edi.
    """
    global SQLITE_PATH, STORAGE_WARNING

    url = _clean(os.getenv("DATABASE_URL"))

    if not url:
        if VOLUME_PATH:
            url = SQLITE_PREFIX + (Path(VOLUME_PATH) / "sano_books.db").as_posix()
        else:
            url = SQLITE_PREFIX + "./sano_books.db"

    if url.startswith("sqlite:///"):
        url = SQLITE_PREFIX + url[len("sqlite:///"):]

    if not url.startswith(SQLITE_PREFIX):
        # Boshqa baza (masalan PostgreSQL) — o'zgartirmaymiz
        return url

    raw = url[len(SQLITE_PREFIX):].split("?", 1)[0]
    if raw in ("", ":memory:"):
        return url

    path = Path(raw)
    if not path.is_absolute():
        if VOLUME_PATH:
            path = Path(VOLUME_PATH) / path.name
        else:
            path = (BASE_DIR / path).resolve()

    SQLITE_PATH = path
    if ON_RAILWAY and not VOLUME_PATH:
        STORAGE_WARNING = (
            "Railway'da Volume ulanmagan: SQLite bazasi vaqtinchalik diskda turibdi va "
            "har deployda O'CHIB KETADI. Service -> Settings -> Volumes orqali /data Volume qo'shing."
        )
    return SQLITE_PREFIX + path.as_posix()


def _prepare_sqlite_file() -> None:
    """Baza papkasini yaratadi. Volume bo'sh bo'lsa va loyiha ichida eski sano_books.db bo'lsa, bir marta nusxalaydi."""
    if SQLITE_PATH is None:
        return
    try:
        SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        bundled = BASE_DIR / "sano_books.db"
        if (
            not SQLITE_PATH.exists()
            and bundled.exists()
            and bundled.resolve() != SQLITE_PATH.resolve()
        ):
            shutil.copy2(bundled, SQLITE_PATH)
    except OSError:
        # Bu yerda xato bo'lsa ham bot ishga tushishi kerak — SQLAlchemy o'zi yangi fayl yaratadi
        pass


DATABASE_URL: str = _resolve_database_url()
_prepare_sqlite_file()


def is_admin(user_id: int) -> bool:
    """Berilgan user_id ADMIN_IDS ro'yxatida ekanini tekshiradi."""
    return user_id in ADMIN_IDS
