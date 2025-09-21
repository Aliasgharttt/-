import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توکن رو از Environment Variable می‌گیریم
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment variables!")

# اپلیکیشن Flask برای Webhook
app = Flask(__name__)

# اپلیکیشن ربات
application = Application.builder().token(TOKEN).build()

# دستورات مدیر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🤖 Bot started successfully!")
    await msg.delete(delay=10)  # پاک شدن بعد از 10 ثانیه

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        msg = await update.message.reply_text("🚫 User banned.")
        await msg.delete(delay=10)

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        msg = await update.message.reply_text("✅ User unbanned.")
        await msg.delete(delay=10)

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            permissions={"can_send_messages": False}
        )
        msg = await update.message.reply_text("🔇 User muted.")
        await msg.delete(delay=10)

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_id = int(context.args[0])
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
            }
        )
        msg = await update.message.reply_text("🔊 User unmuted.")
        await msg.delete(delay=10)

# حذف لینک‌ها
async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "http" in update.message.text:
        await update.message.delete()

# حذف فحاشی (لیست نمونه)
bad_words = ["badword1", "badword2"]

async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(word in text for word in bad_words):
        await update.message.delete()

# هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("unban", unban))
application.add_handler(CommandHandler("mute", mute))
application.add_handler(CommandHandler("unmute", unmute))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_links))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_bad_words))

# ست کردن Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "🤖 Bot is running!"

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )
    app.run(host="0.0.0.0", port=PORT)
