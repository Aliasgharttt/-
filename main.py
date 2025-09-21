import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TOKEN

# حذف خودکار پیام بعد از 10 ثانیه
async def auto_delete(message):
    await asyncio.sleep(10)
    try:
        await message.delete()
    except:
        pass

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "سلام 👋\nمن یک ربات مدیریت گروه هستم.\n\n"
        "ویژگی‌ها:\n"
        "✅ خوشامدگویی\n"
        "✅ حذف لینک\n"
        "✅ حذف فحاشی\n"
        "✅ سایلنس/آن‌سایلنس\n"
        "✅ بن/آن‌بن\n"
        "✅ حذف خودکار پیام‌های ربات بعد از ۱۰ ثانیه\n\n"
        "پشتیبانی: @Aliasghar091a"
    )
    await auto_delete(msg)

# خوشامد
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        msg = await update.message.reply_text(f"خوش اومدی {member.mention_html()} 🎉", parse_mode="HTML")
        await auto_delete(msg)

# حذف لینک
async def remove_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "http" in update.message.text or "t.me" in update.message.text:
        await update.message.delete()

# حذف فحاشی (لیست نمونه)
bad_words = ["کلمه1", "کلمه2", "کلمه3"]

async def remove_badwords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if any(word in update.message.text.lower() for word in bad_words):
        await update.message.delete()

# سایلنس
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("برای سایلنس باید روی پیام کاربر ریپلای کنید.")
    user = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user,
        ChatPermissions(can_send_messages=False)
    )
    msg = await update.message.reply_text("کاربر بی‌صدا شد 🔇")
    await auto_delete(msg)

# آن‌سایلنس
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("برای رفع سایلنس باید روی پیام کاربر ریپلای کنید.")
    user = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user,
        ChatPermissions(can_send_messages=True)
    )
    msg = await update.message.reply_text("کاربر از حالت بی‌صدا خارج شد 🔊")
    await auto_delete(msg)

# بن
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("برای بن باید روی پیام کاربر ریپلای کنید.")
    user = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user)
    msg = await update.message.reply_text("کاربر بن شد 🚫")
    await auto_delete(msg)

# آن‌بن
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("برای رفع بن باید روی پیام کاربر ریپلای کنید.")
    user = update.message.reply_to_message.from_user.id
    await context.bot.unban_chat_member(update.effective_chat.id, user)
    msg = await update.message.reply_text("کاربر رفع بن شد ✅")
    await auto_delete(msg)

# ران اصلی
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, remove_links))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, remove_badwords))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))

    app.run_polling()

if __name__ == "__main__":
    main()
