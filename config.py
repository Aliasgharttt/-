import os

TOKEN = os.getenv("BOT_TOKEN")  # توکن از Environment Variable خونده میشه
PORT = int(os.getenv("PORT", 10000))  # پورت پیش‌فرض 10000
