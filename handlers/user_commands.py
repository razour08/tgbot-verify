"""User command handlers / معالجات أوامر المستخدم"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command
from utils.messages import (
    get_welcome_message,
    get_about_message,
    get_help_message,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /start command"""
    if await reject_group_command(update):
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    full_name = user.full_name or ""

    # Already registered
    if db.user_exists(user_id):
        await update.message.reply_text(
            f"👋 Welcome back, {full_name}!\n"
            "You are already registered.\n"
            "Send /help to see available commands.\n\n"
            f"أهلاً بعودتك، {full_name}!\n"
            "أنت مسجل بالفعل.\n"
            "أرسل /help لعرض الأوامر المتاحة."
        )
        return

    # Invite handling
    invited_by: Optional[int] = None
    if context.args:
        try:
            invited_by = int(context.args[0])
            if not db.user_exists(invited_by):
                invited_by = None
        except Exception:
            invited_by = None

    # Create user
    if db.create_user(user_id, username, full_name, invited_by):
        welcome_msg = get_welcome_message(full_name, bool(invited_by))
        await update.message.reply_text(welcome_msg)
    else:
        await update.message.reply_text(
            "❌ Registration failed, please try again later.\n"
            "فشل التسجيل، يرجى المحاولة لاحقاً."
        )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /about command"""
    if await reject_group_command(update):
        return

    await update.message.reply_text(get_about_message())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /help command"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    await update.message.reply_text(get_help_message(is_admin))


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /balance command"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You are blocked and cannot use this feature.\n"
            "أنت محظور ولا يمكنك استخدام هذه الميزة."
        )
        return

    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text(
            "⚠️ Please register first with /start.\n"
            "يرجى التسجيل أولاً باستخدام /start."
        )
        return

    await update.message.reply_text(
        f"💰 Points Balance / رصيد النقاط\n\n"
        f"Current points / النقاط الحالية: {user['balance']}"
    )


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /qd check-in command"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You are blocked and cannot use this feature.\n"
            "أنت محظور ولا يمكنك استخدام هذه الميزة."
        )
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(
            "⚠️ Please register first with /start.\n"
            "يرجى التسجيل أولاً باستخدام /start."
        )
        return

    # Check if already checked in today
    if not db.can_checkin(user_id):
        await update.message.reply_text(
            "❌ Already checked in today. Come back tomorrow!\n"
            "لقد سجلت دخولك اليوم بالفعل. عُد غداً!"
        )
        return

    # Perform check-in
    if db.checkin(user_id):
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"✅ Check-in successful!\n"
            f"Points earned / نقاط مكتسبة: +1\n"
            f"Current balance / الرصيد الحالي: {user['balance']}"
        )
    else:
        await update.message.reply_text(
            "❌ Already checked in today. Come back tomorrow!\n"
            "لقد سجلت دخولك اليوم بالفعل. عُد غداً!"
        )


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /invite command"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You are blocked and cannot use this feature.\n"
            "أنت محظور ولا يمكنك استخدام هذه الميزة."
        )
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(
            "⚠️ Please register first with /start.\n"
            "يرجى التسجيل أولاً باستخدام /start."
        )
        return

    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        f"🎁 Your invite link / رابط دعوتك:\n{invite_link}\n\n"
        "Each successful invite earns you 2 points.\n"
        "كل دعوة ناجحة تكسبك 2 نقطة."
    )


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /use command - redeem code"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You are blocked and cannot use this feature.\n"
            "أنت محظور ولا يمكنك استخدام هذه الميزة."
        )
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(
            "⚠️ Please register first with /start.\n"
            "يرجى التسجيل أولاً باستخدام /start."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /use <code>\n\n"
            "Example / مثال: /use wandouyu"
        )
        return

    key_code = context.args[0].strip()
    result = db.use_card_key(key_code, user_id)

    if result is None:
        await update.message.reply_text(
            "❌ Code not found. Please check and try again.\n"
            "الكود غير موجود. يرجى التحقق والمحاولة مرة أخرى."
        )
    elif result == -1:
        await update.message.reply_text(
            "❌ This code has reached its usage limit.\n"
            "هذا الكود وصل للحد الأقصى من الاستخدام."
        )
    elif result == -2:
        await update.message.reply_text(
            "❌ This code has expired.\n"
            "هذا الكود منتهي الصلاحية."
        )
    elif result == -3:
        await update.message.reply_text(
            "❌ You have already used this code.\n"
            "لقد استخدمت هذا الكود بالفعل."
        )
    else:
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"✅ Code redeemed successfully!\n"
            f"Points earned / نقاط مكتسبة: {result}\n"
            f"Current balance / الرصيد الحالي: {user['balance']}"
        )
