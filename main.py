import telebot
from flask import Flask, request
import config

bot = telebot.TeleBot(config.TOKEN)
server = Flask(__name__)

# ---------------- دستورات ربات ---------------- #
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, "سلام ✨\nمن رباتت هستم. آماده‌ام برات کار کنم 🚀")

@bot.message_handler(commands=["help"])
def help_message(message):
    bot.reply_to(message, "دستورات موجود:\n/start - شروع\n/help - راهنما")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"شما گفتید: {message.text}")

# ---------------- وبهوک ---------------- #
@server.route(f"/{config.TOKEN}", methods=["POST"])
def webhook():
    update = request.stream.read().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "!", 200

@server.route("/")
def index():
    return "ربات آنلاین است ✅", 200

if __name__ == "__main__":
    # روی Render فقط این کد اجرا میشه
    server.run(host="0.0.0.0", port=config.PORT)
