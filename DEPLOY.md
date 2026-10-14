# 🚂 Railway'ga joylash (SANO BOOKS bot)

## 0. Oldindan
- **Kompyuteringizdagi botni to'xtating** (`Ctrl+C`). Bitta token bilan ikki joyda ishlasa `TelegramConflictError` chiqadi.
- GitHub repo **private** bo'lsin. `.env` va `*.db` fayllar `.gitignore` orqali yuklanmaydi — shunday qoldiring.

## 1. GitHub'ga yuklash
Shu papkaning ichidagi hamma narsani (ichidagi `bot.py` repo ildizida turishi kerak) yangi repoga push qiling.

## 2. Railway'da loyiha
1. railway.com → **New Project → Deploy from GitHub repo** → reponi tanlang.
2. Builder avtomatik (Railpack). `bot.py` ni o'zi topadi, Python versiyasi `.python-version` dan olinadi.
   Agar "No start command" desa: **Settings → Deploy → Custom Start Command** ga `python bot.py` yozing.

## 3. Variables (Service → Variables)
| Nomi | Qiymati |
|---|---|
| `BOT_TOKEN` | @BotFather bergan token |
| `ADMIN_ID` | Telegram ID (bir nechta bo'lsa `ADMIN_IDS=111,222`) |

`DATABASE_URL` ni **qo'shmang** — Volume avtomatik topiladi.

## 4. Volume (MAJBURIY — aks holda har deployda baza o'chadi)
Service → **Settings → Volumes → Add Volume** → Mount path: **`/data`**
(`/app/data` EMAS — u kodingizdagi `data/` papkasini bosib ketadi.)

## 5. Tekshirish (Deployments → View Logs)
Quyidagilar chiqishi kerak:
```
Baza fayli: /data/sano_books.db
SANO BOOKS Telegram Bot started!
```
Keyin Telegram'da botga `/start` yozing.

## 6. Eski bazani (buyurtmalar, foydalanuvchilar) ko'chirish — ixtiyoriy
Eski `sano_books.db` ni loyiha ildiziga qo'yib `git add -f sano_books.db` qiling va push qiling. Bot birinchi ishga tushganda uni Volume'ga **bir marta** nusxalaydi (keyingi deploylarda ustiga yozmaydi). Ko'chgach, faylni repodan olib tashlang — unda mijozlar telefoni va manzillari bor.

## Xatolar
| Logda | Sabab / yechim |
|---|---|
| `BOT_TOKEN sozlanmagan` | Variables ga `BOT_TOKEN` qo'shing |
| `BOT_TOKEN noto'g'ri formatda` | Tokenni @BotFather'dan qayta nusxalang |
| `Railway'da Volume ulanmagan` | 4-qadam: Volume `/data` ga ulang |
| `TelegramConflictError` | Boshqa joyda (lokal / eski deploy) shu token bilan bot ishlayapti |
| `ADMIN_ID sozlanmagan` | Variables ga `ADMIN_ID` qo'shing |

## Eslatma
Bot ma'lumotlarini endi hech qachon avtomatik o'chirmaydi: demo kitoblar faqat baza **butunlay bo'sh** bo'lganda yoziladi.
Qo'lda to'liq qayta yozish kerak bo'lsa: `python data/seed.py --force` (barcha kitob va tugmalar o'chadi!).
