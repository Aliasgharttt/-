import os

# توکن ربات از محیط گرفته میشه (نه مستقیم تو کد!)
TOKEN = os.environ.get("8418297859:AAHH89g2QwsEsmWnmM09bm4hRGfw55FRo18")

# Render خودش PORT رو ست می‌کنه
PORT = int(os.environ.get("PORT", 1000))
