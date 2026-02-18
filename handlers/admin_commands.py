"""Admin command handlers / معالجات أوامر المسؤول"""
import asyncio
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command

logger = logging.getLogger(__name__)


async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /addbalance command - admin add points"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /addbalance <user_id> <points>\n\n"
            "Example / مثال: /addbalance 123456789 10"
        )
        return

    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])

        if not db.user_exists(target_user_id):
            await update.message.reply_text(
                "❌ User not found. / المستخدم غير موجود."
            )
            return

        if db.add_balance(target_user_id, amount):
            user = db.get_user(target_user_id)
            await update.message.reply_text(
                f"✅ Added {amount} points to user {target_user_id}.\n"
                f"تمت إضافة {amount} نقطة للمستخدم {target_user_id}.\n"
                f"Current balance / الرصيد الحالي: {user['balance']}"
            )
        else:
            await update.message.reply_text(
                "❌ Operation failed. Please try again.\n"
                "فشلت العملية. يرجى المحاولة مرة أخرى."
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format. Please enter valid numbers.\n"
            "تنسيق غير صالح. يرجى إدخال أرقام صحيحة."
        )


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /block command - admin block user"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /block <user_id>\n\n"
            "Example / مثال: /block 123456789"
        )
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text(
                "❌ User not found. / المستخدم غير موجود."
            )
            return

        if db.block_user(target_user_id):
            await update.message.reply_text(
                f"✅ User {target_user_id} has been blocked.\n"
                f"تم حظر المستخدم {target_user_id}."
            )
        else:
            await update.message.reply_text(
                "❌ Operation failed. Please try again.\n"
                "فشلت العملية. يرجى المحاولة مرة أخرى."
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format. Please enter a valid user ID.\n"
            "تنسيق غير صالح. يرجى إدخال معرف مستخدم صحيح."
        )


async def white_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /white command - admin unblock user"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /white <user_id>\n\n"
            "Example / مثال: /white 123456789"
        )
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text(
                "❌ User not found. / المستخدم غير موجود."
            )
            return

        if db.unblock_user(target_user_id):
            await update.message.reply_text(
                f"✅ User {target_user_id} has been unblocked.\n"
                f"تم إلغاء حظر المستخدم {target_user_id}."
            )
        else:
            await update.message.reply_text(
                "❌ Operation failed. Please try again.\n"
                "فشلت العملية. يرجى المحاولة مرة أخرى."
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format. Please enter a valid user ID.\n"
            "تنسيق غير صالح. يرجى إدخال معرف مستخدم صحيح."
        )


async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /blacklist command - view blacklist"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    blacklist = db.get_blacklist()

    if not blacklist:
        await update.message.reply_text(
            "📋 Blacklist is empty. / القائمة السوداء فارغة."
        )
        return

    msg = "📋 Blacklist / القائمة السوداء:\n\n"
    for user in blacklist:
        msg += f"User ID / المعرف: {user['user_id']}\n"
        msg += f"Username / اسم المستخدم: @{user['username']}\n"
        msg += f"Name / الاسم: {user['full_name']}\n"
        msg += "---\n"

    await update.message.reply_text(msg)


async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /genkey command - admin create redemption code"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /genkey <code> <points> [uses] [days]\n\n"
            "Examples / أمثلة:\n"
            "/genkey wandouyu 20 - 20pts, single use, no expiry\n"
            "/genkey vip100 50 10 - 50pts, 10 uses, no expiry\n"
            "/genkey temp 30 1 7 - 30pts, single use, expires in 7 days"
        )
        return

    try:
        key_code = context.args[0].strip()
        balance = int(context.args[1])
        max_uses = int(context.args[2]) if len(context.args) > 2 else 1
        expire_days = int(context.args[3]) if len(context.args) > 3 else None

        if balance <= 0:
            await update.message.reply_text(
                "❌ Points must be greater than 0.\n"
                "يجب أن تكون النقاط أكبر من 0."
            )
            return

        if max_uses <= 0:
            await update.message.reply_text(
                "❌ Usage count must be greater than 0.\n"
                "يجب أن يكون عدد الاستخدامات أكبر من 0."
            )
            return

        if db.create_card_key(key_code, balance, user_id, max_uses, expire_days):
            msg = (
                "✅ Code created successfully!\n"
                "تم إنشاء الكود بنجاح!\n\n"
                f"Code / الكود: {key_code}\n"
                f"Points / النقاط: {balance}\n"
                f"Max uses / الاستخدامات: {max_uses}\n"
            )
            if expire_days:
                msg += f"Expires in / ينتهي خلال: {expire_days} days/أيام\n"
            else:
                msg += "Expiry / الصلاحية: Never / دائم\n"
            msg += f"\nUser command / أمر المستخدم: /use {key_code}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text(
                "❌ Code already exists or creation failed. Try a different name.\n"
                "الكود موجود بالفعل أو فشل الإنشاء. جرّب اسماً مختلفاً."
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format. Please enter valid numbers.\n"
            "تنسيق غير صالح. يرجى إدخال أرقام صحيحة."
        )


async def listkeys_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /listkeys command - admin view codes"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    keys = db.get_all_card_keys()

    if not keys:
        await update.message.reply_text(
            "📋 No codes found. / لا توجد أكواد."
        )
        return

    msg = "📋 Code List / قائمة الأكواد:\n\n"
    for key in keys[:20]:
        msg += f"Code / الكود: {key['key_code']}\n"
        msg += f"Points / النقاط: {key['balance']}\n"
        msg += f"Uses / الاستخدامات: {key['current_uses']}/{key['max_uses']}\n"

        if key["expire_at"]:
            expire_time = datetime.fromisoformat(key["expire_at"])
            if datetime.now() > expire_time:
                msg += "Status / الحالة: Expired / منتهي\n"
            else:
                days_left = (expire_time - datetime.now()).days
                msg += f"Status / الحالة: Active ({days_left} days left) / نشط ({days_left} يوم)\n"
        else:
            msg += "Status / الحالة: Permanent / دائم\n"

        msg += "---\n"

    if len(keys) > 20:
        msg += f"\n(Showing first 20 of {len(keys)} / عرض أول 20 من {len(keys)})"

    await update.message.reply_text(msg)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /broadcast command - admin broadcast"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 You don't have permission to use this command.\n"
            "ليس لديك صلاحية لاستخدام هذا الأمر."
        )
        return

    text = " ".join(context.args).strip() if context.args else ""
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text or ""

    if not text:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /broadcast <text>\n"
            "Or reply to a message and send /broadcast\n"
            "أو قم بالرد على رسالة وأرسل /broadcast"
        )
        return

    user_ids = db.get_all_user_ids()
    success, failed = 0, 0

    status_msg = await update.message.reply_text(
        f"📢 Broadcasting to {len(user_ids)} users...\n"
        f"جارِ الإرسال إلى {len(user_ids)} مستخدم..."
    )

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning("Broadcast to %s failed: %s", uid, e)
            failed += 1

    await status_msg.edit_text(
        f"✅ Broadcast complete! / اكتمل الإرسال!\n"
        f"Success / نجاح: {success}\n"
        f"Failed / فشل: {failed}"
    )
