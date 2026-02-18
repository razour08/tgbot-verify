"""Verification command handlers / معالجات أوامر التحقق"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message

# Try to import concurrency control
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


# ============================================================
# Common bilingual messages / رسائل مشتركة ثنائية اللغة
# ============================================================

MSG_BLOCKED = (
    "🚫 You are blocked and cannot use this feature.\n"
    "أنت محظور ولا يمكنك استخدام هذه الميزة."
)

MSG_NOT_REGISTERED = (
    "⚠️ Please register first with /start.\n"
    "يرجى التسجيل أولاً باستخدام /start."
)

MSG_INVALID_LINK = (
    "❌ Invalid SheerID link. Please check and try again.\n"
    "رابط SheerID غير صالح. يرجى التحقق والمحاولة مرة أخرى."
)

MSG_DEDUCT_FAILED = (
    "❌ Failed to deduct points. Please try again later.\n"
    "فشل خصم النقاط. يرجى المحاولة لاحقاً."
)


def msg_refunded(cost):
    return (
        f"Points refunded / تم استرداد النقاط: +{cost}"
    )


def msg_verify_failed(error, cost):
    return (
        f"❌ Verification failed / فشل التحقق: {error}\n\n"
        f"{msg_refunded(cost)}"
    )


def msg_process_error(error, cost):
    return (
        f"❌ Error during processing / خطأ أثناء المعالجة: {error}\n\n"
        f"{msg_refunded(cost)}"
    )


def msg_success_result(result, service_name):
    result_msg = (
        f"✅ {service_name} verification successful!\n"
        f"✅ نجح تحقق {service_name}!\n\n"
    )
    if result.get("pending"):
        result_msg += (
            "✨ Document submitted, awaiting SheerID review.\n"
            "تم تقديم المستند، بانتظار مراجعة SheerID.\n"
            "⏱️ Expected review time: a few minutes.\n"
            "الوقت المتوقع: بضع دقائق.\n\n"
        )
    if result.get("redirect_url"):
        result_msg += f"🔗 Redirect link / رابط التوجيه:\n{result['redirect_url']}"
    return result_msg


def msg_processing(service_name, cost, extra=""):
    return (
        f"⏳ Processing {service_name} verification...\n"
        f"جارِ معالجة تحقق {service_name}...\n\n"
        f"Points deducted / نقاط مخصومة: -{cost}\n"
        f"{extra}"
        "Please wait 1-2 minutes... / يرجى الانتظار 1-2 دقيقة..."
    )


# ============================================================
# Verify Commands
# ============================================================

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify - Gemini One Pro"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text(MSG_INVALID_LINK)
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text(MSG_DEDUCT_FAILED)
        return

    processing_msg = await update.message.reply_text(
        msg_processing("Gemini One Pro", VERIFY_COST,
                       f"Verification ID: {verification_id}\n")
    )

    try:
        verifier = OneVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            await processing_msg.edit_text(
                msg_success_result(result, "Gemini One Pro")
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                msg_verify_failed(result.get('message', 'Unknown error'), VERIFY_COST)
            )
    except Exception as e:
        logger.error("Gemini verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify2 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text(MSG_INVALID_LINK)
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text(MSG_DEDUCT_FAILED)
        return

    processing_msg = await update.message.reply_text(
        msg_processing("ChatGPT Teacher K12", VERIFY_COST,
                       f"Verification ID: {verification_id}\n")
    )

    try:
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            await processing_msg.edit_text(
                msg_success_result(result, "ChatGPT Teacher K12")
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                msg_verify_failed(result.get('message', 'Unknown error'), VERIFY_COST)
            )
    except Exception as e:
        logger.error("ChatGPT K12 verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify3 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text(MSG_INVALID_LINK)
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text(MSG_DEDUCT_FAILED)
        return

    processing_msg = await update.message.reply_text(
        f"🎵 Processing Spotify Student verification...\n"
        f"جارِ معالجة تحقق Spotify Student...\n\n"
        f"Points deducted / نقاط مخصومة: -{VERIFY_COST}\n\n"
        "📝 Generating student info / إنشاء معلومات الطالب...\n"
        "🎨 Generating student ID PNG / إنشاء بطاقة الطالب...\n"
        "📤 Submitting documents / تقديم المستندات..."
    )

    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            await processing_msg.edit_text(
                msg_success_result(result, "Spotify Student")
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                msg_verify_failed(result.get('message', 'Unknown error'), VERIFY_COST)
            )
    except Exception as e:
        logger.error("Spotify verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify4 - Bolt.new Teacher (auto-fetch code)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text(MSG_INVALID_LINK)
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text(MSG_DEDUCT_FAILED)
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Processing Bolt.new Teacher verification...\n"
        f"جارِ معالجة تحقق Bolt.new Teacher...\n\n"
        f"Points deducted / نقاط مخصومة: -{VERIFY_COST}\n"
        "📤 Submitting documents / تقديم المستندات..."
    )

    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Document submission failed / فشل تقديم المستند: "
                f"{result.get('message', 'Unknown error')}\n\n"
                f"{msg_refunded(VERIFY_COST)}"
            )
            return

        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Could not get verification ID / لم يتم الحصول على معرف التحقق\n\n"
                f"{msg_refunded(VERIFY_COST)}"
            )
            return

        await processing_msg.edit_text(
            f"✅ Document submitted! / تم تقديم المستند!\n"
            f"📋 Verification ID: `{vid}`\n\n"
            f"🔍 Auto-fetching verification code...\n"
            f"جارِ جلب كود التحقق تلقائياً...\n"
            f"(Max wait / انتظار أقصى: 20s)"
        )

        # Auto-fetch verification code
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)

        if code:
            result_msg = (
                f"🎉 Verification successful! / نجح التحقق!\n\n"
                f"✅ Document submitted / تم تقديم المستند\n"
                f"✅ Review passed / تمت الموافقة\n"
                f"✅ Code obtained / تم الحصول على الكود\n\n"
                f"🎁 Verification code / كود التحقق: `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Redirect / توجيه:\n{result['redirect_url']}"

            await processing_msg.edit_text(result_msg)

            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid
            )
        else:
            await processing_msg.edit_text(
                f"✅ Document submitted successfully!\n"
                f"تم تقديم المستند بنجاح!\n\n"
                f"⏳ Code not generated yet (review may take 1-5 min).\n"
                f"لم يتم إنشاء الكود بعد (المراجعة قد تستغرق 1-5 دقائق).\n\n"
                f"📋 Verification ID: `{vid}`\n\n"
                f"💡 Query later with / استعلم لاحقاً بـ:\n"
                f"`/getV4Code {vid}`\n\n"
                f"Note: Points already deducted. Later queries are free.\n"
                f"ملاحظة: تم خصم النقاط. الاستعلام اللاحق مجاني."
            )

            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review",
                vid
            )

    except Exception as e:
        logger.error("Bolt.new verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5
) -> Optional[str]:
    """Auto-fetch verification code (lightweight polling)

    Args:
        verification_id: Verification ID
        max_wait: Maximum wait time in seconds
        interval: Polling interval in seconds

    Returns:
        str: Verification code, or None if not found
    """
    import time
    start_time = time.time()
    attempts = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1

            if elapsed >= max_wait:
                logger.info(f"Auto-fetch code timed out ({elapsed}s)")
                return None

            try:
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )

                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")

                    if current_step == "success":
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ Auto-fetch code success: {code} ({elapsed}s)")
                            return code
                    elif current_step == "error":
                        logger.warning(f"Review failed: {data.get('errorIds', [])}")
                        return None

                await asyncio.sleep(interval)

            except Exception as e:
                logger.warning(f"Code query error: {e}")
                await asyncio.sleep(interval)

    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /verify5 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text(MSG_INVALID_LINK)
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text(MSG_DEDUCT_FAILED)
        return

    processing_msg = await update.message.reply_text(
        f"📺 Processing YouTube Student Premium verification...\n"
        f"جارِ معالجة تحقق YouTube Student Premium...\n\n"
        f"Points deducted / نقاط مخصومة: -{VERIFY_COST}\n\n"
        "📝 Generating student info / إنشاء معلومات الطالب...\n"
        "🎨 Generating student ID PNG / إنشاء بطاقة الطالب...\n"
        "📤 Submitting documents / تقديم المستندات..."
    )

    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            await processing_msg.edit_text(
                msg_success_result(result, "YouTube Student Premium")
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                msg_verify_failed(result.get('message', 'Unknown error'), VERIFY_COST)
            )
    except Exception as e:
        logger.error("YouTube verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /getV4Code - Get Bolt.new Teacher verification code"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /getV4Code <verification_id>\n\n"
            "Example / مثال: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "The verification_id is provided after using /verify4.\n"
            "يتم توفير معرف التحقق بعد استخدام /verify4."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Querying verification code, please wait...\n"
        "جارِ الاستعلام عن كود التحقق، يرجى الانتظار..."
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Query failed. Status code: {response.status_code}\n"
                    f"فشل الاستعلام. رمز الحالة: {response.status_code}\n\n"
                    "Please try again later or contact admin.\n"
                    "يرجى المحاولة لاحقاً أو التواصل مع المسؤول."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = (
                    "✅ Verification successful! / نجح التحقق!\n\n"
                    f"� Code / الكود: `{reward_code}`\n\n"
                )
                if redirect_url:
                    result_msg += f"🔗 Redirect / توجيه:\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ Verification still under review. Please try again later.\n"
                    "التحقق لا يزال قيد المراجعة. يرجى المحاولة لاحقاً.\n\n"
                    "Usually takes 1-5 minutes. / عادةً تستغرق 1-5 دقائق."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    f"❌ Verification failed / فشل التحقق\n\n"
                    f"Error / خطأ: {', '.join(error_ids) if error_ids else 'Unknown / غير معروف'}"
                )
            else:
                await processing_msg.edit_text(
                    f"⚠️ Current status / الحالة الحالية: {current_step}\n\n"
                    "Code not generated yet. Please try again later.\n"
                    "لم يتم إنشاء الكود بعد. يرجى المحاولة لاحقاً."
                )

    except Exception as e:
        logger.error("Bolt.new code fetch failed: %s", e)
        await processing_msg.edit_text(
            f"❌ Error during query / خطأ أثناء الاستعلام: {str(e)}\n\n"
            "Please try again later or contact admin.\n"
            "يرجى المحاولة لاحقاً أو التواصل مع المسؤول."
        )
