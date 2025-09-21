# config.py
import os

# مقدار توکن از VAR گرفته می‌شود — در Render: KEY = BOT_TOKEN , VALUE = your_token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# پورت را از Render یا مقدار پیش‌فرض می‌گیریم
PORT = int(os.environ.get("PORT", 10000))

# آدرس بیرونی (Render) برای ست کردن webhook
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
# مثلاً: "https://mdyryt-grwh.onrender.com"

# شناسه پشتیبانی که ربات بعد از استارت پیام می‌دهد (مثال)
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "@Aliasghar091a")
