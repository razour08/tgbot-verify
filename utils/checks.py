"""التحقق من الصلاحيات والتحقق من صحتها (Permission checks and validation)"""
import logging
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME

logger = logging.getLogger(__name__)


def is_group_chat(update: Update) -> bool:
    """التحقق مما إذا كانت المحادثة جماعية"""
    chat = update.effective_chat
    return chat and chat.type in ("group", "supergroup")


async def reject_group_command(update: Update) -> bool:
    """قيود المجموعة: السماح فقط بأوامر التحقق وتسجيل الدخول"""
    if is_group_chat(update):
        await update.message.reply_text(
            "⚠️ Group chat only supports /verify /verify2 /verify3 /verify4 /verify5 /qd.\n"
            "Please use other commands in private chat.\n\n"
            "المحادثة الجماعية تدعم فقط أوامر التحقق و /qd.\n"
            "يرجى استخدام الأوامر الأخرى في المحادثة الخاصة."
        )
        return True
    return False


async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """التحقق من عضوية المستخدم في القناة"""
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error("Channel membership check failed: %s", e)
        return False
