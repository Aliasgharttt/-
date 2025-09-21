# config.import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # از Environment Variables می‌خونه
PORT = int(os.getenv("PORT", 10000))
URL = os.getenv("RENDER_URL")  # آدرس پروژه روی Render
