import os
import re
import telebot
from flask import Flask, request
from threading import Timer

# =====================
# تنظیمات
# =====================
TOKEN = os.getenv("BOT_TOKEN")  # توکن باید توی Render → Environment Variable ست بشه
if not TOKEN:
    TOKEN = "توکن_اینجا"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =====================
# توابع کمکی
# =====================
def delete_later(chat_id, message_id, delay=10):
    """حذف پیام بعد از چند ثانیه"""
    Timer(delay, lambda: bot.delete_message(chat_id, message_id)).start()

def is_admin(chat_id, user_id):
    """بررسی اینکه کاربر ادمین گروه هست یا نه"""
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# =====================
# هندلر استارت
# =====================
@bot.message_handler(commands=["start"])
def send_start(message):
    txt = "سلام 👋\nمن ربات مدیریت گروه هستم.\n\n" \
          "📌 /help → راهنما\n" \
          "📌 /support → پشتیبانی"
    sent = bot.reply_to(message, txt)
    delete_later(sent.chat.id, sent.message_id)

@bot.message_handler(commands=["help"])
def send_help(message):
    txt = "📖 راهنمای ربات:\n\n" \
          "🔹 ریپلای کنید و دستور بزنید:\n" \
          " /ban → بن\n" \
          " /unban → رفع بن\n" \
          " /mute → بیصدا\n" \
          " /unmute → رفع بیصدا"
    sent = bot.reply_to(message, txt)
    delete_later(sent.chat.id, sent.message_id)

@bot.message_handler(commands=["support"])
def send_support(message):
    txt = "📩 برای پشتیبانی با مدیر تماس بگیرید."
    sent = bot.reply_to(message, txt)
    delete_later(sent.chat.id, sent.message_id)

# =====================
# مدیریت لینک و تبلیغات
# =====================
@bot.message_handler(func=lambda m: True)
def filter_links(message):
    if re.search(r"(https?://|t\.me/|www\.)", message.text or "", re.IGNORECASE):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

# =====================
# دستورات مدیریتی
# =====================
@bot.message_handler(commands=["ban", "unban", "mute", "unmute"])
def admin_actions(message):
    if not message.reply_to_message:
        sent = bot.reply_to(message, "❗️باید روی پیام کاربر ریپلای کنید.")
        delete_later(sent.chat.id, sent.message_id)
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id

    if not is_admin(chat_id, user_id):
        sent = bot.reply_to(message, "🚫 فقط مدیران می‌توانند از این دستور استفاده کنند.")
        delete_later(sent.chat.id, sent.message_id)
        return

    cmd = message.text.split()[0].lower()

    try:
        if cmd == "/ban":
            bot.ban_chat_member(chat_id, target_id)
            resp = bot.reply_to(message, "✅ کاربر بن شد.")
        elif cmd == "/unban":
            bot.unban_chat_member(chat_id, target_id)
            resp = bot.reply_to(message, "✅ کاربر رفع بن شد.")
        elif cmd == "/mute":
            bot.restrict_chat_member(chat_id, target_id, can_send_messages=False)
            resp = bot.reply_to(message, "🔇 کاربر بی‌صدا شد.")
        elif cmd == "/unmute":
            bot.restrict_chat_member(chat_id, target_id, can_send_messages=True)
            resp = bot.reply_to(message, "🔊 کاربر از بی‌صدا خارج شد.")

        delete_later(resp.chat.id, resp.message_id)
    except Exception as e:
        sent = bot.reply_to(message, f"⚠️ خطا: {e}")
        delete_later(sent.chat.id, sent.message_id)

# =====================
# وبهوک
# =====================
@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "ربات فعال است ✅", 200

# =====================
# اجرا
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
