import os
from flask import Flask, request
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# ساختن اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()


# ------------------ دستورات ادمین ------------------
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.message.chat_id, user_id)
        await update.message.reply_text("✅ User banned")


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.message.chat_id, user_id)
        await update.message.reply_text("✅ User unbanned")


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        perms = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(update.message.chat_id, user_id, permissions=perms)
        await update.message.reply_text("🔇 User muted")


async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        perms = ChatPermissions(can_send_messages=True)
        await context.bot.restrict_chat_member(update.message.chat_id, user_id, permissions=perms)
        await update.message.reply_text("🔊 User unmuted")


# اضافه کردن دستورات
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("unban", unban))
application.add_handler(CommandHandler("mute", mute))
application.add_handler(CommandHandler("unmute", unmute))


# ------------------ Flask Webhook ------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"


@app.route("/")
def index():
    return "Bot is running!"


if __name__ == "__main__":
    # ست کردن وبهوک
    application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
