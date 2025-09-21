from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from config import TOKEN

# دیکشنری برای مدیریت اسپم
user_messages = {}

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 👋\n"
        "من ربات مدیریت گروه هستم ✅\n\n"
        "قابلیت‌ها:\n"
        "🔹 پیام خوشامد خودکار (و حذف بعد ۱۰ ثانیه)\n"
        "🔹 ضد اسپم (۱۰ پیام در ۱۰ ثانیه → بی‌صدا)\n"
        "🔹 بن کردن کاربر با دستور /ban\n"
        "🔹 رفع بن با دستور /unban\n"
        "🔹 بی‌صدا کردن با دستور /mute\n"
        "🔹 رفع بی‌صدا با دستور /unmute\n\n"
        "📞 پشتیبانی: @Aliasghar091a"
    )
    await update.message.reply_text(text)

# پیام خوشامد
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        msg = await update.message.reply_text(f"خوش آمدی {member.first_name} 🌹")
        await asyncio.sleep(10)
        try:
            await msg.delete()
        except:
            pass

# ضد اسپم (بیش از 10 پیام در 10 ثانیه → میوت)
async def check_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(update.message.date.timestamp())

    # فقط 10 ثانیه آخر نگه داریم
    user_messages[user_id] = [t for t in user_messages[user_id] if t > update.message.date.timestamp() - 10]

    if len(user_messages[user_id]) > 10:
        try:
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(can_send_messages=False),
                until_date=update.message.date.timestamp() + 60
            )
            await update.message.reply_text("⛔️ کاربر به دلیل اسپم، موقتا بی‌صدا شد (۱ دقیقه)")
        except:
            pass

# دستور /ban
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کاربر ریپلای کنید و دستور /ban بزنید ❗️")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.message.chat_id, user_id)
        await update.message.reply_text("🚫 کاربر بن شد")
    except:
        await update.message.reply_text("خطا در بن ❌")

# دستور /unban
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ایدی عددی کاربر را وارد کنید: /unban 123456")
        return
    user_id = int(context.args[0])
    try:
        await context.bot.unban_chat_member(update.message.chat_id, user_id)
        await update.message.reply_text("✅ کاربر آن‌بن شد")
    except:
        await update.message.reply_text("خطا در آن‌بن ❌")

# دستور /mute
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کاربر ریپلای کنید و دستور /mute بزنید ❗️")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.restrict_chat_member(
            update.message.chat_id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text("🔇 کاربر بی‌صدا شد")
    except:
        await update.message.reply_text("خطا در بی‌صدا ❌")

# دستور /unmute
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کاربر ریپلای کنید و دستور /unmute بزنید ❗️")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.restrict_chat_member(
            update.message.chat_id,
            user_id,
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        )
        await update.message.reply_text("🔊 کاربر از بی‌صدا خارج شد")
    except:
        await update.message.reply_text("خطا در رفع بی‌صدا ❌")

# ران اصلی
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_spam))

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))

    app.run_polling()

if __name__ == "__main__":
    main()
