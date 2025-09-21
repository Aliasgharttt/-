from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
import asyncio
import config

# لاگ
logging.basicConfig(level=logging.INFO)

# ساخت ربات
bot = Bot(token=config.TOKEN)
application = Application.builder().token(config.TOKEN).build()

# دستور استارت
async def start(update: Update, context):
    await update.message.reply_text("✅ ربات مدیریت گروه فعال شد\n\nپشتیبانی: @Aliasghar091a")

# هندلرها
application.add_handler(CommandHandler("start", start))

# حذف لینک
async def remove_links(update: Update, context):
    if "http" in update.message.text:
        try:
            await update.message.delete()
        except:
            pass

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, remove_links))

# Flask برای Webhook
app = Flask(__name__)

@app.route(f"/{config.TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT)
