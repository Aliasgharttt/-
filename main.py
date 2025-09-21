import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import config

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات مدیریت گروه آماده‌ست ✅")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("روی یک پیام ریپلای کن ❗")
    await update.message.chat.ban_member(update.message.reply_to_message.from_user.id)
    await update.message.reply_text("کاربر بن شد 🚫")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("ایدی عددی کاربر رو بده ❗")
    user_id = int(context.args[0])
    await update.message.chat.unban_member(user_id)
    await update.message.reply_text("کاربر آنبن شد ✅")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("روی یک پیام ریپلای کن ❗")
    perms = update.message.chat.permissions
    await update.message.chat.restrict_member(
        update.message.reply_to_message.from_user.id,
        permissions=perms.__class__(can_send_messages=False)
    )
    await update.message.reply_text("کاربر میوت شد 🔇")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("روی یک پیام ریپلای کن ❗")
    perms = update.message.chat.permissions
    await update.message.chat.restrict_member(
        update.message.reply_to_message.from_user.id,
        permissions=perms.__class__(can_send_messages=True)
    )
    await update.message.reply_text("کاربر آنمیوت شد 🔊")

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("روی یک پیام ریپلای کن ❗")
    await update.message.chat.ban_member(update.message.reply_to_message.from_user.id)
    await update.message.chat.unban_member(update.message.reply_to_message.from_user.id)
    await update.message.reply_text("کاربر کیک شد 👢")

# Message filter
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "کلمه بد" in text:  # اینو می‌تونی تغییر بدی
        await update.message.delete()
        await update.message.reply_text("پیام نامناسب حذف شد ❌")

# Main
def main():
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not set in env")

    app = Application.builder().token(config.BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
    app.add_handler(CommandHandler("kick", kick_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    # Webhook
    webhook_url = (config.URL.rstrip("/") + f"/{config.BOT_TOKEN}") if config.URL else None

    app.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    main()
