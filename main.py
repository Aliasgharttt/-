import os
import re
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from config import TOKEN

# حذف پیام بعد از چند ثانیه
async def delete_later(context: ContextTypes.DEFAULT_TYPE, message_id, chat_id, delay=10):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id, message_id)
    except:
        pass

# پیام خوشامدگویی
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            msg = await update.message.reply_text(f"Welcome {member.mention_html()} 👋",
                                                  parse_mode="HTML")
            asyncio.create_task(delete_later(context, msg.message_id, msg.chat_id))

# حذف لینک
async def delete_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if re.search(r"(http[s]?://|t\.me|www\.)", update.message.text, re.IGNORECASE):
        try:
            await update.message.delete()
        except:
            pass

# حذف فحاشی (لیست نمونه)
BAD_WORDS = ["fuck", "shit", "koskhol", "khar"]

async def delete_bad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(word in text for word in BAD_WORDS):
        try:
            await update.message.delete()
        except:
            pass

# پشتیبانی (دستور /start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Support: @Aliasghar091a")
    asyncio.create_task(delete_later(context, msg.message_id, msg.chat_id))

# بن کاربر
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        msg = await update.message.reply_text("User banned ✅")
        asyncio.create_task(delete_later(context, msg.message_id, msg.chat_id))

# رفع بن
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        msg = await update.message.reply_text("User unbanned ✅")
        asyncio.create_task(delete_later(context, msg.message_id, msg.chat_id))

# بی‌صدا
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        permissions = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions=permissions)
        msg = await update.message.reply_text("User muted 🔇")
        asyncio.create_task(delete_later(context, msg.message_id, msg.chat_id))

# رفع بی‌صدا
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        permissions = ChatPermissions(can_send_messages=True,
                                      can_send_media_messages=True,
                                      can_send_other_messages=True,
                                      can_add_web_page_previews=True)
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions=permissions)
        msg = await update.message.reply_text("User unmuted 🔊")
        asyncio.create_task(delete_later(context, msg.message_id, msg.chat_id))

# ------------------------
# راه‌اندازی ربات (Webhook)
# ------------------------
PORT = int(os.environ.get("PORT", 8443))
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_links))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_bad))

# Webhook
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"
)
