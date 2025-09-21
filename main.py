import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # توی Render متغیر محیطی ست کن
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # همون آدرس render + /webhook/TOKEN

app = Flask(__name__)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# دستورات ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات فعاله ✅")

application.add_handler(CommandHandler("start", start))

# مسیر وبهوک برای دریافت آپدیت‌ها
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# ست کردن وبهوک روی استارت
@app.before_first_request
def set_webhook():
    import requests
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook/{TOKEN}"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
