"""Message Templates / قوالب الرسائل"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Get welcome message / رسالة الترحيب"""
    msg = (
        f"🎉 Welcome, {full_name}!\n"
        "You have been registered and received 1 point.\n"
        f"\n🎉 مرحباً، {full_name}!\n"
        "تم تسجيلك بنجاح وحصلت على 1 نقطة.\n"
    )
    if invited_by:
        msg += (
            "Thanks for joining via invite link. The inviter received 2 points.\n"
            "شكراً للانضمام عبر رابط الدعوة. حصل الداعي على 2 نقطة.\n"
        )

    msg += (
        "\n🤖 This bot can auto-complete SheerID verification.\n"
        "هذا البوت يُكمل تحقق SheerID تلقائياً.\n"
        "\n📌 Quick Start / البدء السريع:\n"
        "/about - Bot features / ميزات البوت\n"
        "/balance - Points balance / رصيد النقاط\n"
        "/help - Full command list / قائمة الأوامر\n\n"
        "💰 Earn Points / اكسب النقاط:\n"
        "/qd - Daily check-in / تسجيل الدخول اليومي\n"
        "/invite - Invite friends / دعوة الأصدقاء\n"
        f"📺 Channel / القناة: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Get about message / رسالة حول البوت"""
    return (
        "🤖 SheerID Auto-Verification Bot\n"
        "بوت التحقق التلقائي من SheerID\n"
        "\n"
        "📋 Features / الميزات:\n"
        "- Auto-complete SheerID student/teacher verification\n"
        "  إكمال تحقق الطلاب/المعلمين تلقائياً\n"
        "- Supports: Gemini One Pro, ChatGPT Teacher K12, Spotify Student, YouTube Student, Bolt.new Teacher\n"
        "\n"
        "💰 Earn Points / اكسب النقاط:\n"
        "- Registration / التسجيل: +1 point/نقطة\n"
        "- Daily check-in / تسجيل يومي: +1 point/نقطة\n"
        "- Invite friends / دعوة أصدقاء: +2 points/نقطة per person\n"
        "- Redemption codes / أكواد الاسترداد\n"
        f"- Join channel / انضم للقناة: {CHANNEL_URL}\n"
        "\n"
        "📖 How to use / طريقة الاستخدام:\n"
        "1. Start verification on the website and copy the full link\n"
        "   ابدأ التحقق على الموقع وانسخ الرابط الكامل\n"
        "2. Send /verify, /verify2, /verify3, /verify4 or /verify5 with the link\n"
        "   أرسل الأمر مع الرابط\n"
        "3. Wait for processing and check results\n"
        "   انتظر المعالجة وتحقق من النتائج\n"
        "4. Bolt.new auto-fetches code. Manual query: /getV4Code <verification_id>\n"
        "   Bolt.new يجلب الكود تلقائياً. استعلام يدوي: /getV4Code\n"
        "\n"
        "More commands / المزيد: /help"
    )


def get_help_message(is_admin: bool = False) -> str:
    """Get help message / رسالة المساعدة"""
    msg = (
        "📖 SheerID Bot - Help / المساعدة\n"
        "\n"
        "👤 User Commands / أوامر المستخدم:\n"
        "/start - Register / التسجيل\n"
        "/about - Bot features / ميزات البوت\n"
        "/balance - Points balance / رصيد النقاط\n"
        "/qd - Daily check-in (+1) / تسجيل يومي\n"
        "/invite - Invite link (+2/person) / رابط دعوة\n"
        "/use <code> - Redeem code / استرداد كود\n"
        f"/verify <link> - Gemini One Pro (-{VERIFY_COST}pt)\n"
        f"/verify2 <link> - ChatGPT Teacher K12 (-{VERIFY_COST}pt)\n"
        f"/verify3 <link> - Spotify Student (-{VERIFY_COST}pt)\n"
        f"/verify4 <link> - Bolt.new Teacher (-{VERIFY_COST}pt)\n"
        f"/verify5 <link> - YouTube Student Premium (-{VERIFY_COST}pt)\n"
        "/getV4Code <id> - Get Bolt.new code / كود Bolt.new\n"
        "/help - This help / هذه المساعدة\n"
        f"❓ Troubleshooting / استكشاف الأخطاء: {HELP_NOTION_URL}\n"
    )

    if is_admin:
        msg += (
            "\n🔧 Admin Commands / أوامر المسؤول:\n"
            "/addbalance <user_id> <points> - Add points / إضافة نقاط\n"
            "/block <user_id> - Block user / حظر مستخدم\n"
            "/white <user_id> - Unblock user / إلغاء حظر\n"
            "/blacklist - View blacklist / القائمة السوداء\n"
            "/genkey <code> <points> [uses] [days] - Create code / إنشاء كود\n"
            "/listkeys - View codes / عرض الأكواد\n"
            "/broadcast <text> - Broadcast / إرسال جماعي\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Get insufficient balance message / رسالة رصيد غير كافي"""
    return (
        f"⚠️ Insufficient points! Need {VERIFY_COST}, have {current_balance}.\n"
        f"نقاط غير كافية! مطلوب {VERIFY_COST}، لديك {current_balance}.\n\n"
        "💰 Earn points / اكسب نقاط:\n"
        "- /qd - Daily check-in / تسجيل يومي\n"
        "- /invite - Invite friends / دعوة أصدقاء\n"
        "- /use <code> - Redeem code / استرداد كود"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Get verify usage message / رسالة استخدام التحقق"""
    return (
        f"📖 Usage / الاستخدام: {command} <SheerID link>\n\n"
        "Example / مثال:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "How to get the link / كيف تحصل على الرابط:\n"
        f"1. Visit {service_name} verification page\n"
        f"   قم بزيارة صفحة تحقق {service_name}\n"
        "2. Start verification process / ابدأ عملية التحقق\n"
        "3. Copy the full URL from browser / انسخ الرابط الكامل\n"
        f"4. Submit with {command} / أرسل باستخدام {command}"
    )
