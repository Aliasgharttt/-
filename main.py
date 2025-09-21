# main.py
import asyncio
import re
from collections import deque, defaultdict
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config

# ---------- SETTINGS ----------
WELCOME_DELETE_AFTER = 10  # seconds — حذف پیام خوشامد بعد از 10s
BOT_MESSAGE_DELETE_AFTER = 10  # همه پیام‌های ربات بعد از 10s حذف شوند
SPAM_WINDOW = 10  # seconds
SPAM_LIMIT = 10  # بیش از 10 پیام در SPAM_WINDOW -> موقت بی‌صدا
SPAM_MUTE_DURATION = 60  # mute seconds when spam detected
PROFANITY = {"فحش1", "فحش2"}  # لیست نمونه؛ خودت پر کن
LINK_REGEX = re.compile(r"https?://\S+|t\.me/\S+|telegram\.me/\S+")

# track user messages timestamps per chat
user_msg_times = defaultdict(lambda: defaultdict(deque))
# store last bot messages to auto-delete (chat_id -> deque of (msg_id, when))
bot_messages = defaultdict(deque)


# ---------- HELPERS ----------
async def is_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False


async def schedule_delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id, message_id)
    except:
        pass


async def track_and_check_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_chat:
        return False
    uid = update.effective_user.id
    cid = update.effective_chat.id
    now = datetime.utcnow().timestamp()
    dq = user_msg_times[cid][uid]
    dq.append(now)
    # pop old
    while dq and now - dq[0] > SPAM_WINDOW:
        dq.popleft()
    if len(dq) > SPAM_LIMIT:
        return True
    return False


async def try_delete_if_bot_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # هر پیام ارسالی توسط ربات (مثلاً reply به /start) را حذف کن
    msg = update.effective_message
    if not msg:
        return
    if msg.from_user and msg.from_user.is_bot:
        # schedule delete
        asyncio.create_task(schedule_delete_message(context, msg.chat_id, msg.message_id, BOT_MESSAGE_DELETE_AFTER))


# ---------- HANDLERS ----------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    text = f"سلام {user.mention_html()}!\nاین ربات برای مدیریت گروه ساخته شده — هر مشکلی بود پشتیبانی: {config.SUPPORT_USERNAME}"
    sent = await update.message.reply_html(text)
    # delete the welcome after WELCOME_DELETE_AFTER seconds
    asyncio.create_task(schedule_delete_message(context, sent.chat_id, sent.message_id, WELCOME_DELETE_AFTER))
    # also delete the user's /start message after short time (optional)
    try:
        asyncio.create_task(schedule_delete_message(context, update.effective_chat.id, update.message.message_id, WELCOME_DELETE_AFTER))
    except:
        pass


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return
    # expects reply to a user
    if not update.message.reply_to_message:
        await update.message.reply_text("لطفاً روی پیام کاربر ریپلای کنید و دستور /ban را بفرستید.")
        return
    target = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, target.id)
    await update.message.reply_text(f"{target.full_name} بن شد.")
    # delete bot message after delay
    sent = await update.message.reply_text("کار انجام شد.")
    asyncio.create_task(schedule_delete_message(context, sent.chat_id, sent.message_id, BOT_MESSAGE_DELETE_AFTER))


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return
    if not context.args:
        await update.message.reply_text("برای آنبن، از /unban <user_id> یا ریپلای استفاده کنید.")
        return
    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        sent = await update.message.reply_text("آن‌بن شد.")
        asyncio.create_task(schedule_delete_message(context, sent.chat_id, sent.message_id, BOT_MESSAGE_DELETE_AFTER))
    except Exception as e:
        await update.message.reply_text("خطا در آنبن کردن: " + str(e))


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("لطفاً روی پیام کاربر ریپلای کنید و دستور /mute را بفرستید.")
        return
    try:
        target = update.message.reply_to_message.from_user
        until = datetime.utcnow() + timedelta(seconds=SPAM_MUTE_DURATION)
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until,
        )
        sent = await update.message.reply_text(f"{target.full_name} بی‌صدا شد به مدت {SPAM_MUTE_DURATION} ثانیه.")
        asyncio.create_task(schedule_delete_message(context, sent.chat_id, sent.message_id, BOT_MESSAGE_DELETE_AFTER))
    except Exception as e:
        await update.message.reply_text("خطا: " + str(e))


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("لطفاً روی پیام کاربر ریپلای کنید و دستور /unmute را بفرستید.")
        return
    target = update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        target.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
        ),
    )
    sent = await update.message.reply_text(f"{target.full_name} دوباره فعال شد.")
    asyncio.create_task(schedule_delete_message(context, sent.chat_id, sent.message_id, BOT_MESSAGE_DELETE_AFTER))


async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("فقط مدیران می‌توانند این دستور را اجرا کنند.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("لطفاً روی پیام کاربر ریپلای کنید و دستور /kick را بفرستید.")
        return
    target = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, target.id)
    await context.bot.unban_chat_member(update.effective_chat.id, target.id)  # kick (ban then unban) 
    sent = await update.message.reply_text(f"{target.full_name} از گروه اخراج شد.")
    asyncio.create_task(schedule_delete_message(context, sent.chat_id, sent.message_id, BOT_MESSAGE_DELETE_AFTER))


# ---------- message handler: moderation ----------
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not update.effective_chat:
        return

    # 1) اگر پیام از ربات بود، حذف زودهنگامش کن
    if msg.from_user and msg.from_user.is_bot:
        asyncio.create_task(schedule_delete_message(context, msg.chat_id, msg.message_id, BOT_MESSAGE_DELETE_AFTER))
        return

    # 2) لینک -> حذف و اخطار
    if LINK_REGEX.search(msg.text or ""):
        try:
            await msg.delete()
            info = await msg.reply_text("لینک‌ها مجاز نیست — پیام حذف شد.")
            asyncio.create_task(schedule_delete_message(context, info.chat_id, info.message_id, BOT_MESSAGE_DELETE_AFTER))
            return
        except:
            pass

    # 3) فحاشی -> حذف
    text = (msg.text or "").lower()
    for bad in PROFANITY:
        if bad in text:
            try:
                await msg.delete()
                info = await msg.reply_text("زبان محترمانه استفاده کنید — پیام حذف شد.")
                asyncio.create_task(schedule_delete_message(context, info.chat_id, info.message_id, BOT_MESSAGE_DELETE_AFTER))
                return
            except:
                pass

    # 4) اسپم: بیش از X پیام در Y ثانیه -> temporary mute
    is_spam = await track_and_check_spam(update, context)
    if is_spam:
        # mute user temporarily
        uid = msg.from_user.id
        until = datetime.utcnow() + timedelta(seconds=SPAM_MUTE_DURATION)
        try:
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                uid,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until,
            )
            info = await msg.reply_text("شما برای مدتی کوتاه بی‌صدا شدید (رفتار اسپم).")
            asyncio.create_task(schedule_delete_message(context, info.chat_id, info.message_id, BOT_MESSAGE_DELETE_AFTER))
        except:
            pass


# ---------- startup ----------
def main():
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not set in env")

    app = Application.builder().token(config.BOT_TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
    app.add_handler(CommandHandler("kick", kick_command))

    # all text messages (moderation)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    # run as webhook
    webhook_path = f"/{config.BOT_TOKEN}"
    webhook_url = (config.RENDER_EXTERNAL_URL.rstrip("/") + webhook_path) if config.RENDER_EXTERNAL_URL else None

    # run webhook server (builtin aiohttp) — listen on 0.0.0.0:PORT
    app.run_webhook(
        listen="0.0.0.0",
        port=config.PORT,
        webhook_url=webhook_url,
        webhook_path=webhook_path,
    )


if __name__ == "__main__":
    main()
