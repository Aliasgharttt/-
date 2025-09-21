from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import config

app = Flask(__name__)

# ---------------------------
# دستور /start
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات با موفقیت بالا اومد 🚀")

# ---------------------------
# ست کردن ربات تلگرام
# ---------------------------
application = Application.builder().token(config.BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# ---------------------------
# Webhook
# ---------------------------
@app.route(f"/{config.BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def home():
    return "ربات روی Render بالا اومد ✅"

if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        url_path=config.BOT_TOKEN,
        webhook_url=f"{config.URL}/{config.BOT_TOKEN}"
    )
