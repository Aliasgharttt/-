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

# 📌 لیست کلمات بد
BAD_WORDS = ["کلمه1", "کلمه2", "کلمه3"]  # اینجا کلمات رو خودت پر کن

# 📌 ذخیره پیام‌ها برای ضد اسپم
user_messages = {}

# 📌 خوشامد به کاربر جدید
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for member in message.new_chat_members:
        sent = bot.send_message(
            message.chat.id,
            f"👋 خوش آمدی {member.first_name} به گروه!"
        )
        delete_later(sent.chat.id, sent.message_id)

# 📌 فیلتر لینک‌ها
@bot.message_handler(func=lambda msg: bool(re.search(r"http[s]?://|t\.me", msg.text or "")))
def filter_links(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# 📌 فیلتر کلمات بد
@bot.message_handler(func=lambda msg: any(bad in (msg.text or "").lower() for bad in BAD_WORDS))
def filter_bad_words(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# 📌 ضد اسپم (بیش از 10 پیام در 10 ثانیه → بیصدا 1 دقیقه)
@bot.message_handler(func=lambda msg: True)
def anti_spam(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = time.time()

    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < 10]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > 10:
        try:
            bot.restrict_chat_member(
                chat_id, user_id,
                until_date=int(time.time()) + 60,  # 1 دقیقه
                can_send_messages=False
            )
            sent = bot.send_message(chat_id, f"🚫 {message.from_user.first_name} به علت اسپم، 1 دقیقه بیصدا شد.")
            delete_later(sent.chat.id, sent.message_id)
        except:
            pass

# 📌 دستور start
@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.reply_to(
        message,
        "سلام 👋\nمن ربات مدیریت گروه هستم.\n\n"
        "📌 قابلیت‌ها:\n"
        "🔹 فیلتر لینک و کلمات بد\n"
        "🔹 خوشامد به عضو جدید\n"
        "🔹 ریپلای مدیران: بن، رفع‌بن، بیصدا، رفع‌بیصدا\n"
        "🔹 سیستم گزارش کاربران\n"
        "🔹 ضد اسپم (ارسال زیاد پیام → سکوت خودکار)\n\n"
        "📖 برای جزئیات دستورها: /help\n\n"
        "☎️ پشتیبانی: @Aliasghar091a"
    )
    delete_later(sent.chat.id, sent.message_id)

# 📌 دستور help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    sent = bot.reply_to(
        message,
        "📖 راهنمای ربات:\n\n"
        "▫️ ریپلای با متن 'بن' = بن کاربر ❌\n"
        "▫️ ریپلای با متن 'رفع بن' = آزاد کردن کاربر ✅\n"
        "▫️ ریپلای با متن 'بیصدا' = میوت کردن کاربر 🔇\n"
        "▫️ ریپلای با متن 'رفع بیصدا' = آزاد کردن از میوت 🔊\n"
        "▫️ ریپلای با متن 'گزارش' = ارسال پیام به مدیران 📢\n\n"
        "⚡ ضد اسپم: اگر کاربری بیش از 10 پیام در 10 ثانیه بفرستد → 1 دقیقه بیصدا می‌شود.\n\n"
        "☎️ پشتیبانی: @Aliasghar091a"
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

# 📌 سیستم گزارش برای کاربران
@bot.message_handler(func=lambda msg: msg.reply_to_message and msg.text.lower() == "گزارش")
def report_user(message):
    admins = bot.get_chat_administrators(message.chat.id)
    for admin in admins:
        try:
            bot.forward_message(admin.user.id, message.chat.id, message.reply_to_message.message_id)
            bot.send_message(admin.user.id, f"📢 گزارش توسط {message.from_user.first_name}")
        except:
            pass

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
