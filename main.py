import telebot
import re
import time
import threading
from flask import Flask, request
from config import TOKEN, WEBHOOK_URL

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📌 حذف پیام ربات بعد از 10 ثانیه
def delete_later(chat_id, message_id, delay=10):
    def job():
        time.sleep(delay)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    threading.Thread(target=job).start()

# 📌 فیلتر لینک‌ها
@bot.message_handler(func=lambda msg: bool(re.search(r"http[s]?://|t\.me", msg.text or "")))
def filter_links(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# 📌 دستور start
@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.reply_to(
        message,
        "سلام 👋\nمن ربات مدیریت گروه هستم.\n\n"
        "دستورات من:\n"
        "🔹 /help راهنما\n"
        "🔹 ریپلای روی کاربر: بن، رفع‌بن، بیصدا، رفع‌بیصدا"
    )
    delete_later(sent.chat.id, sent.message_id)

# 📌 دستور help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    sent = bot.reply_to(
        message,
        "📖 راهنمای ربات:\n\n"
        "▫️ ریپلای با متن 'بن' = بن کاربر\n"
        "▫️ ریپلای با متن 'رفع بن' = آزاد کردن کاربر\n"
        "▫️ ریپلای با متن 'بیصدا' = میوت کردن کاربر\n"
        "▫️ ریپلای با متن 'رفع بیصدا' = آزاد کردن از میوت"
    )
    delete_later(sent.chat.id, sent.message_id)

# 📌 مدیریت گروه با ریپلای مدیران
@bot.message_handler(func=lambda msg: msg.reply_to_message and msg.text.lower() in ["بن", "رفع بن", "بیصدا", "رفع بیصدا"])
def admin_actions(message):
    if not message.from_user.id in [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)]:
        return  # فقط مدیران

    target = message.reply_to_message.from_user.id

    if message.text.lower() == "بن":
        bot.kick_chat_member(message.chat.id, target)
        sent = bot.reply_to(message, "کاربر بن شد ❌")
    elif message.text.lower() == "رفع بن":
        bot.unban_chat_member(message.chat.id, target)
        sent = bot.reply_to(message, "کاربر رفع بن شد ✅")
    elif message.text.lower() == "بیصدا":
        bot.restrict_chat_member(message.chat.id, target, can_send_messages=False)
        sent = bot.reply_to(message, "کاربر بیصدا شد 🔇")
    elif message.text.lower() == "رفع بیصدا":
        bot.restrict_chat_member(message.chat.id, target, can_send_messages=True)
        sent = bot.reply_to(message, "کاربر رفع بیصدا شد 🔊")

    delete_later(sent.chat.id, sent.message_id)

# 📌 وبهوک
@app.route("/webhook", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
