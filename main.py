import re
import logging
import threading
from flask import Flask, request
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN, PORT

# فعال‌سازی لاگ
logging.basicConfig(level=logging.INFO)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# اپ Flask برای وبهوک
app = Flask(__name__)

# --- دستورات مدیریتی ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "این ربات مخصوص مدیریت گروه است.\n\n"
        "📌 دستورات مدیر:\n"
        " - /ban (با ریپلای) = بن کاربر\n"
        " - /unban (با ریپلای) = رفع بن\n"
        " - /mute (با ریپلای) = بی‌صدا کردن\n"
        " - /unmute (با ریپلای) = رفع بی‌صدا\n\n"
        "ℹ️ پشتیبانی: @Aliasghar091a"
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        msg = await update.message.reply_text(f"🚫 کاربر {user.first_name} بن شد.")
        threading.Timer(10, lambda: context.application.create_task(msg.delete())).start()

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        msg = await update.message.reply_text(f"✅ کاربر {user.first_name} رفع بن شد.")
        threading.Timer(10, lambda: context.application.create_task(msg.delete())).start()

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        permissions = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
        msg = await update.message.reply_text(f"🔇 کاربر {user.first_name} بی‌صدا شد.")
        threading.Timer(10, lambda: context.application.create_task(msg.delete())).start()

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        permissions = ChatPermissions(can_send_messages=True)
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
        msg = await update.message.reply_text(f"🔊 کاربر {user.first_name} رفع بی‌صدا شد.")
        threading.Timer(10, lambda: context.application.create_task(msg.delete())).start()

# --- حذف لینک و فحاشی ---
BAD_WORDS = ["کلمه_بد1", "کلمه_بد2", "کلمه_بد3"]

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if re.search(r"(https?://\S+)", text):  # لینک
        await update.message.delete()
    elif any(bad_word in text for bad_word in BAD_WORDS):  # فحش
        await update.message.delete()

# --- حذف پیام ربات بعد از 10 ثانیه ---
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.from_user.is_bot:  # فقط پیام‌های ربات
        threading.Timer(10, lambda: context.application.create_task(msg.delete())).start()

# --- هندلرها ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("unban", unban))
application.add_handler(CommandHandler("mute", mute))
application.add_handler(CommandHandler("unmute", unmute))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))
application.add_handler(MessageHandler(filters.ALL, auto_delete))

# --- Flask routes ---
@app.route("/")
def home():
    return "ربات مدیریت گروه فعال است ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
