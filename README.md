# 🏆 Leader-Board

## 📌 Loyihaning qisqacha tavsifi

**🛍️ MarketBot** — bu Telegram boti boʻlib, foydalanuvchilarga mahsulotlarni koʻrib chiqish, buyurtma berish va
toʻlovlarni amalga oshirish imkonini beradi. Click.uz to'lov tizimi. U Aiogram 3 bilan qurilgan, ma'lumotlarni saqlash uchun 
PostgreSQL-dan foydalanadi va bir nechta tillarni (o'zbek, rus) qo'llab-quvvatlaydi.

## ⚙️ Asosiy xususiyatlar

- **Aiogram**:Python’da yozilgan asinxron Telegram botlarini yaratish uchun yengil va tezkor framework .
- **Docker**: Ilovani konteynerlash va uni turli muhitlarda ishlatish imkonini beradi.
- **Alembic**: SQLAlchemy uchun ma’lumotlar bazasi migratsiyalarini boshqarish vositasi.
- **Starlette Admin**: Starlette yoki FastAPI asosida ma’lumotlar bazasi uchun admin panel yaratish vositasi.
- **CLick.uz**:Tolov tizimi masovaviy tolov qilish uchun.

## 🛠 Texnologiyalar

| Texnologiya | Tavsifi                                                      |
|-------------|--------------------------------------------------------------|
| Python 3.12 | Asosiy dasturlash tili                                       |
| Aiogram3    | Telegram botlarini yaratish uchun yengil va tezkor framework |
| PostgreSQL  | Ma’lumotlar bazasi                                           |
| Docker      | Konteynerizatsiya                                            |

## 🛠️ O'rnatish va ishga tushirish

1. Repositoriyani klonlash

```bash
git clone https://github.com/XojaxonovPY/MarketBot.git
cd MarketBot
```

2. Virtual muhit yaratish va kutubxonalarni o'rnatish

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Docker yordamida ishga tushirish

```bash
docker-compose up --build
```

4. Ma'lumotlar bazasini migratsiya qilish

```bash
alembic revision --autogenerate -m "Create a baseline migrations"
alembic upgrade head
```

5. Ilovani ishga tushirish

```bash
python main.py
```

6. Admin panelni ishga tushirish

```bash
uvicorn web.app:app --host localhost --port 8000
```

## 🔧 .env konfiguratsiyasi

Ilova ishlashi uchun `.env` faylida quyidagi parametrlarni sozlash kerak:

```env
BOT_TOKEN=Your_bot_token
PAYMENT_CLICK_TOKEN=Your click token
DP_NAME=Your_db_name
DP_USER=Your_db_username
DP_PASSWORD=Your_db_password
DP_HOST=Your_db_host
DP_PORT=Your_db_port
DP_ASYNC_URL=postgresql+asyncpg://db_user:password@host:port/db_name
DP_SYNC_URL=postgresql+psycopg2://db_user:password@host:port/db_name
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
```

## 📄 Litsenziya

Loyiha MIT litsenziyasi asosida tarqatiladi.
