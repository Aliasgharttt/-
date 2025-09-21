import re
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from config import TOKEN

# لیست فحاشی
BAD_WORDS = ["کلمه1", "کلمه2", "کلمه3"]  # کلمات بد رو اینجا اضافه کن

# --- بررسی ادمین ---
async def is_admin(update: Update, context: CallbackContext) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]

# --- شروع ---
async def start(update: Update, context: CallbackContext):
    text = (
        "👋 سلام! من ربات مدیریت گروه هستم.\n\n"
        "📌 قابلیت‌ها:\n"
        "1️⃣ خوشامدگویی خودکار (پاک بعد ۱۰ ثانیه)\n"
        "2️⃣ حذف لینک‌ها و فحاشی\n"
        "3️⃣ /ban [id] → بن کردن کاربر\n"
        "4️⃣ /unban [id] → رفع بن\n"
        "5️⃣ /mute [id] → بی‌صدا کردن کاربر\n"
        "6️⃣ /unmute [id] → رفع بی‌صدا\n\n"
        "🛠 فقط مدیرها می‌توانند از دستورات مدیریتی استفاده کنند."
    )
    msg = await update.message.reply_text(text)
    await asyncio.sleep(10)
    await msg.delete()

# --- خوشامدگویی ---
async def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        msg = await update.message.reply_text(f"🎉 خوش آمدی {member.first_name}!")
        await asyncio.sleep(10)
        await msg.delete()

# --- حذف لینک و فحاشی ---
async def filter_messages(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    if "http" in text or "www" in text or re.search(r"\.ir|\.com", text):
        await update.message.delete()
        return

    for bad in BAD_WORDS:
        if bad in text:
            await update.message.delete()
            return

# --- بن ---
async def ban(update: Update, context: CallbackContext):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 فقط مدیرها می‌توانند از این دستور استفاده کنند.")
        return
    if context.args:
        target_id = int(context.args[0])
        await context.bot.ban_chat_member(update.effective_chat.id, target_id)
        await update.message.reply_text("✅ کاربر بن شد.")
    else:
        await update.message.reply_text("❌ لطفا آی‌دی کاربر را وارد کنید.")

# --- رفع بن ---
async def unban(update: Update, context: CallbackContext):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 فقط مدیرها می‌توانند از این دستور استفاده کنند.")
        return
    if context.args:
        target_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, target_id)
        await update.message.reply_text("✅ کاربر رفع بن شد.")
    else:
        await update.message.reply_text("❌ لطفا آی‌دی کاربر را وارد کنید.")

# --- بی‌صدا ---
async def mute(update: Update, context: CallbackContext):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 فقط مدیرها می‌توانند از این دستور استفاده کنند.")
        return
    if context.args:
        target_id = int(context.args[0])
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target_id,
            ChatPermissions(can_send_messages=False),
        )
        await update.message.reply_text("🔇 کاربر بی‌صدا شد.")
    else:
        await update.message.reply_text("❌ لطفا آی‌دی کاربر را وارد کنید.")

# --- رفع بی‌صدا ---
async def unmute(update: Update, context: CallbackContext):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 فقط مدیرها می‌توانند از این دستور استفاده کنند.")
        return
    if context.args:
        target_id = int(context.args[0])
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target_id,
            ChatPermissions(can_send_messages=True),
        )
        await update.message.reply_text("🔊 کاربر رفع بی‌صدا شد.")
    else:
        await update.message.reply_text("❌ لطفا آی‌دی کاربر را وارد کنید.")

# --- اجرای ربات ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
