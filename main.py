from flask import Flask, request
import telebot
import config

bot = telebot.TeleBot(config.BOT_TOKEN)
app = Flask(__name__)

# هندلر استارت
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "ربات با موفقیت فعاله ✅")

# دریافت پیام‌ها از تلگرام
@app.route("/" + config.BOT_TOKEN, methods=["POST"])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# ست کردن وبهوک
@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{config.URL}/{config.BOT_TOKEN}")
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT)
