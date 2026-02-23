"""البرنامج الرئيسي لروبوت (Bot) تيليجرام"""
import logging
from functools import partial

from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from database_mysql import Database
from handlers.user_commands import (
    start_command,
    about_command,
    help_command,
    balance_command,
    checkin_command,
    invite_command,
    use_command,
    status_command,
)
from handlers.verify_commands import (
    verify_command,
    verify2_command,
    verify3_command,
    verify4_command,
    verify5_command,
    getV4Code_command,
    check_command,
)
from handlers.admin_commands import (
    addbalance_command,
    block_command,
    white_command,
    blacklist_command,
    genkey_command,
    listkeys_command,
    broadcast_command,
)

# تكوين السجلات (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """معالجة الأخطاء العامة"""
    logger.exception("حدث استثناء أثناء معالجة التحديث: %s", context.error, exc_info=context.error)


def main():
    """الدالة الرئيسية"""
    # تهيئة قاعدة البيانات
    db = Database()

    # إنشاء التطبيق - تمكين المعالجة المتزامنة (concurrent processing)
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  # 🔥 هام: تمكين المعالجة المتزامنة لأوامر متعددة
        .build()
    )

    # تسجيل أوامر المستخدم (باستخدام partial لتمرير وسيطة db)
    application.add_handler(CommandHandler("start", partial(start_command, db=db)))
    application.add_handler(CommandHandler("about", partial(about_command, db=db)))
    application.add_handler(CommandHandler("help", partial(help_command, db=db)))
    application.add_handler(CommandHandler("balance", partial(balance_command, db=db)))
    application.add_handler(CommandHandler("qd", partial(checkin_command, db=db)))
    application.add_handler(CommandHandler("invite", partial(invite_command, db=db)))
    application.add_handler(CommandHandler("use", partial(use_command, db=db)))
    application.add_handler(CommandHandler("status", partial(status_command, db=db)))

    # تسجيل أوامر التحقق
    application.add_handler(CommandHandler("verify", partial(verify_command, db=db)))
    application.add_handler(CommandHandler("verify2", partial(verify2_command, db=db)))
    application.add_handler(CommandHandler("verify3", partial(verify3_command, db=db)))
    application.add_handler(CommandHandler("verify4", partial(verify4_command, db=db)))
    application.add_handler(CommandHandler("verify5", partial(verify5_command, db=db)))
    application.add_handler(CommandHandler("getV4Code", partial(getV4Code_command, db=db)))
    application.add_handler(CommandHandler("check", partial(check_command, db=db)))

    # تسجيل أوامر المسؤول (Admin)
    application.add_handler(CommandHandler("addbalance", partial(addbalance_command, db=db)))
    application.add_handler(CommandHandler("block", partial(block_command, db=db)))
    application.add_handler(CommandHandler("white", partial(white_command, db=db)))
    application.add_handler(CommandHandler("blacklist", partial(blacklist_command, db=db)))
    application.add_handler(CommandHandler("genkey", partial(genkey_command, db=db)))
    application.add_handler(CommandHandler("listkeys", partial(listkeys_command, db=db)))
    application.add_handler(CommandHandler("broadcast", partial(broadcast_command, db=db)))

    # تسجيل معالج الأخطاء
    application.add_error_handler(error_handler)

    logger.info("جاري بدء تشغيل الروبوت...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
