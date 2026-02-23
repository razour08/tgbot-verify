"""معالجات أوامر التحقق (Verification command handlers)"""
import asyncio
import logging
import httpx
import time
from typing import Optional, Dict

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

# محاولة استيراد التحكم في التزامن (Concurrency control)
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


def _clean_error(result):
    """استخراج رسالة خطأ واضحة (clean) من نتيجة المُدقق (verifier)."""
    if isinstance(result, dict):
        # محاولة الحصول على systemErrorMessage أولاً
        sys_err = result.get("systemErrorMessage", "")
        if sys_err:
            # استخراج الجزء المفيد (مثال: "can not perform step 'X'")
            return sys_err

        # محاولة الحصول على errorIds
        error_ids = result.get("errorIds", [])
        if error_ids:
            return ", ".join(error_ids)

        # محاولة الحصول على حقل message
        msg = result.get("message", "")
        if msg and len(msg) < 200:
            return msg

        # محاولة الحصول على currentStep
        step = result.get("currentStep", "")
        if step == "error":
            return "Verification rejected by SheerID / تم رفض التحقق من SheerID"

    # الاحتياطي (Fallback): إذا كانت سلسلة نصية، قصها إذا كانت أطول من اللازم
    error_str = str(result) if not isinstance(result, str) else result
    if len(error_str) > 150:
        return "Verification rejected / تم رفض التحقق"
    return error_str


def msg_verify_failed(error, cost):
    clean = _clean_error(error) if isinstance(error, dict) else str(error)
    # قص السلسلة إذا كانت لا تزال أطول من اللازم
    if len(clean) > 200:
        clean = clean[:200] + "..."
    return (
        f"❌ Verification failed / فشل التحقق\n\n"
        f"Reason / السبب: {clean}\n\n"
        f"{msg_refunded(cost)}"
    )


def msg_process_error(error, cost):
    return (
        f"❌ Error during processing / خطأ أثناء المعالجة: {error}\n\n"
        f"{msg_refunded(cost)}"
    )


def msg_processing(service_name, cost, extra=""):
    return (
        f"⏳ Processing {service_name} verification...\n"
        f"جارِ معالجة تحقق {service_name}...\n\n"
        f"Points deducted / نقاط مخصومة: -{cost}\n"
        f"{extra}"
        "Please wait 1-2 minutes... / يرجى الانتظار 1-2 دقيقة..."
    )


# ============================================================
# Shared polling helpers
# ============================================================

async def _poll_sheerid_result(
    verification_id: str,
    max_wait: int = 60,
    interval: int = 10
) -> Optional[Dict]:
    """الاستعلام المستمر (Poll) عن واجهة برمجة تطبيقات SheerID للحصول على نتيجة التحقق النهائية.

    Args:
        verification_id: معرّف التحقق الخاص بـ SheerID
        max_wait: أقصى مدة انتظار بالثواني (الافتراضي: 60 ثانية)
        interval: الفاصل الزمني للاستعلام بالثواني

    Returns:
        قاموس (dict) يحتوي على المفاتيح: step, redirect_url, reward_code — أو None عند انتهاء مهلة الاتصال (timeout) أو حدوث خطأ
    """
    start_time = time.time()

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            if elapsed >= max_wait:
                logger.info(f"Poll timed out for {verification_id} ({elapsed}s)")
                return None

            try:
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )

                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")

                    if current_step == "success":
                        return {
                            "step": "success",
                            "redirect_url": data.get("redirectUrl"),
                            "reward_code": (
                                data.get("rewardCode")
                                or data.get("rewardData", {}).get("rewardCode")
                            ),
                        }
                    elif current_step == "error":
                        logger.warning(f"Review failed: {data.get('errorIds', [])}")
                        return {"step": "error", "error_ids": data.get("errorIds", [])}

                # لا يزال معلقاً (Pending)، انتظر وأعد المحاولة
                await asyncio.sleep(interval)

            except Exception as e:
                logger.warning(f"Poll error: {e}")
                await asyncio.sleep(interval)

    return None


async def _handle_success_with_polling(
    processing_msg, result, verification_id, service_name, user_id, db, v_type, url
):
    """معالجة نتيجة التحقق الناجحة، مع الاستعلام المستمر (polling) إذا كانت الحالة معلقة."""

    # إذا كان رابط التوجيه (redirect_url) موجوداً، اعرضه فوراً
    if result.get("redirect_url") and not result.get("pending"):
        result_msg = (
            f"✅ {service_name} verification successful!\n"
            f"✅ نجح تحقق {service_name}!\n\n"
            f"🔗 Redirect link / رابط التفعيل:\n{result['redirect_url']}"
        )
        await processing_msg.edit_text(result_msg)
        db.add_verification(user_id, v_type, url, "success", str(result), verification_id)
        return

    # معلّق (Pending) — إبلاغ المستخدم بأننا ننتظر وبدء الاستعلام المستمر
    await processing_msg.edit_text(
        f"✅ {service_name} — document submitted!\n"
        f"تم تقديم مستند {service_name}!\n\n"
        "⏳ Waiting for SheerID review (up to 60s)...\n"
        "بانتظار مراجعة SheerID (حتى 60 ثانية)...\n\n"
        f"📋 Verification ID: `{verification_id}`"
    )

    poll_result = await _poll_sheerid_result(verification_id, max_wait=60, interval=10)

    if poll_result and poll_result.get("step") == "success":
        redirect = poll_result.get("redirect_url")
        code = poll_result.get("reward_code")

        result_msg = (
            f"🎉 {service_name} verification approved!\n"
            f"تمت الموافقة على تحقق {service_name}!\n\n"
        )
        if redirect:
            result_msg += f"🔗 Activation link / رابط التفعيل:\n{redirect}\n\n"
        if code:
            result_msg += f"🎁 Code / الكود: `{code}`\n"

        await processing_msg.edit_text(result_msg)
        db.add_verification(user_id, v_type, url, "success", str(poll_result), verification_id)

    elif poll_result and poll_result.get("step") == "error":
        db.add_balance(user_id, VERIFY_COST)
        error_ids = poll_result.get("error_ids", [])
        await processing_msg.edit_text(
            f"❌ {service_name} — review rejected / تم رفض المراجعة\n\n"
            f"Error / خطأ: {', '.join(error_ids) if error_ids else 'Unknown'}\n\n"
            f"{msg_refunded(VERIFY_COST)}"
        )
        db.add_verification(user_id, v_type, url, "failed", str(poll_result), verification_id)

    else:
        # انتهاء مهلة الاتصال (Timed out) — الحفظ كمعلق (Pending)، الطلب من المستخدم التحقق لاحقاً
        await processing_msg.edit_text(
            f"✅ {service_name} — document submitted!\n"
            f"تم تقديم المستند بنجاح!\n\n"
            "⏳ Review still in progress.\n"
            "المراجعة لا تزال جارية.\n\n"
            f"📋 Verification ID: `{verification_id}`\n\n"
            "💡 Check later with / تحقق لاحقاً بـ:\n"
            f"`/check {verification_id}`\n\n"
            "Note: Points already deducted. Later checks are free.\n"
            "ملاحظة: تم خصم النقاط. التحقق اللاحق مجاني."
        )
        db.add_verification(user_id, v_type, url, "pending", "Waiting for review", verification_id)


# ============================================================
# أوامر التحقق (Verify Commands)
# ============================================================

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /verify - الخاص بـ Gemini One Pro"""
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

        if result["success"]:
            await _handle_success_with_polling(
                processing_msg, result, verification_id,
                "Gemini One Pro", user_id, db, "gemini_one_pro", url
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            db.add_verification(user_id, "gemini_one_pro", url, "failed", str(result))
            await processing_msg.edit_text(
                msg_verify_failed(result, VERIFY_COST)
            )
    except Exception as e:
        logger.error("Gemini verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /verify2 - الخاص بـ ChatGPT Teacher K12"""
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

        if result["success"]:
            await _handle_success_with_polling(
                processing_msg, result, verification_id,
                "ChatGPT Teacher K12", user_id, db, "chatgpt_teacher_k12", url
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            db.add_verification(user_id, "chatgpt_teacher_k12", url, "failed", str(result))
            await processing_msg.edit_text(
                msg_verify_failed(result, VERIFY_COST)
            )
    except Exception as e:
        logger.error("ChatGPT K12 verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /verify3 - الخاص بـ Spotify Student"""
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

        if result["success"]:
            await _handle_success_with_polling(
                processing_msg, result, verification_id,
                "Spotify Student", user_id, db, "spotify_student", url
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            db.add_verification(user_id, "spotify_student", url, "failed", str(result))
            await processing_msg.edit_text(
                msg_verify_failed(result, VERIFY_COST)
            )
    except Exception as e:
        logger.error("Spotify verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /verify4 - الخاص بـ Bolt.new Teacher (جلب تلقائي للكود)"""
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
            f"(Max wait / انتظار أقصى: 60s)"
        )

        # جلب تلقائي (Auto-fetch) باستخدام مساعد الاستعلام المشترك
        poll_result = await _poll_sheerid_result(vid, max_wait=60, interval=10)

        if poll_result and poll_result.get("step") == "success":
            code = poll_result.get("reward_code")
            redirect = poll_result.get("redirect_url")

            result_msg = (
                f"🎉 Verification successful! / نجح التحقق!\n\n"
                f"✅ Document submitted / تم تقديم المستند\n"
                f"✅ Review passed / تمت الموافقة\n"
            )
            if code:
                result_msg += f"✅ Code obtained / تم الحصول على الكود\n\n"
                result_msg += f"🎁 Verification code / كود التحقق: `{code}`\n"
            if redirect:
                result_msg += f"\n🔗 Redirect / توجيه:\n{redirect}"

            await processing_msg.edit_text(result_msg)
            db.add_verification(user_id, "bolt_teacher", url, "success",
                                f"Code: {code}" if code else str(poll_result), vid)
        else:
            await processing_msg.edit_text(
                f"✅ Document submitted successfully!\n"
                f"تم تقديم المستند بنجاح!\n\n"
                f"⏳ Code not generated yet (review may take 1-5 min).\n"
                f"لم يتم إنشاء الكود بعد (المراجعة قد تستغرق 1-5 دقائق).\n\n"
                f"📋 Verification ID: `{vid}`\n\n"
                f"💡 Query later with / استعلم لاحقاً بـ:\n"
                f"`/check {vid}`\n\n"
                f"Note: Points already deducted. Later queries are free.\n"
                f"ملاحظة: تم خصم النقاط. الاستعلام اللاحق مجاني."
            )
            db.add_verification(user_id, "bolt_teacher", url, "pending",
                                "Waiting for review", vid)

    except Exception as e:
        logger.error("Bolt.new verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /verify5 - الخاص بـ YouTube Student Premium"""
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

        if result["success"]:
            await _handle_success_with_polling(
                processing_msg, result, verification_id,
                "YouTube Student Premium", user_id, db, "youtube_student", url
            )
        else:
            db.add_balance(user_id, VERIFY_COST)
            db.add_verification(user_id, "youtube_student", url, "failed", str(result))
            await processing_msg.edit_text(
                msg_verify_failed(result, VERIFY_COST)
            )
    except Exception as e:
        logger.error("YouTube verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            msg_process_error(str(e), VERIFY_COST)
        )


# ============================================================
# أمر الفحص العام (يعمل مع جميع الخدمات)
# ============================================================

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /check - الاستعلام عن حالة أي تحقق من خلال المعرّف (ID)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text(MSG_BLOCKED)
        return

    if not db.user_exists(user_id):
        await update.message.reply_text(MSG_NOT_REGISTERED)
        return

    if not context.args:
        await update.message.reply_text(
            "📖 Usage / الاستخدام: /check <verification_id>\n\n"
            "Example / مثال: /check 6929436b50d7dc18638890d0\n\n"
            "The verification_id is shown after any verification.\n"
            "يظهر معرف التحقق بعد أي عملية تحقق."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Querying verification status, please wait...\n"
        "جارِ الاستعلام عن حالة التحقق، يرجى الانتظار..."
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
            current_step = data.get("currentStep", "unknown")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")
            rejection_reasons = data.get("rejectionReasons", [])
            error_ids = data.get("errorIds", [])
            segment = data.get("segment", "")
            estimated_review = data.get("estimatedReviewTime", "")
            max_review = data.get("maxReviewTime", "")
            created_ts = data.get("created")
            updated_ts = data.get("updated")

            # -- بناء كتلة المعلومات المعروضة في جميع الخطوات --
            info_lines = []
            info_lines.append(f"📌 Step / الخطوة: {current_step}")
            if segment:
                info_lines.append(f"👤 Segment / الفئة: {segment}")
            if rejection_reasons:
                reasons_str = ", ".join(rejection_reasons)
                info_lines.append(f"🚫 Rejection / سبب الرفض: {reasons_str}")
            if error_ids:
                info_lines.append(f"⚠️ Errors / أخطاء: {', '.join(error_ids)}")
            if estimated_review:
                info_lines.append(f"⏱ Estimated review / وقت المراجعة: {estimated_review}")
            if max_review:
                info_lines.append(f"⏳ Max review / الحد الأقصى: {max_review}")
            if created_ts:
                from datetime import datetime, timezone
                try:
                    created_dt = datetime.fromtimestamp(created_ts / 1000, tz=timezone.utc)
                    info_lines.append(f"📅 Created / أُنشئ: {created_dt.strftime('%Y-%m-%d %H:%M UTC')}")
                except Exception:
                    pass
            if updated_ts:
                try:
                    updated_dt = datetime.fromtimestamp(updated_ts / 1000, tz=timezone.utc)
                    info_lines.append(f"🔄 Updated / آخر تحديث: {updated_dt.strftime('%Y-%m-%d %H:%M UTC')}")
                except Exception:
                    pass

            info_block = "\n".join(info_lines)

            # -- معالجة كل خطوة --
            if current_step == "success":
                result_msg = "✅ Verification successful! / نجح التحقق!\n\n"
                if redirect_url:
                    result_msg += f"🔗 Activation link / رابط التفعيل:\n{redirect_url}\n\n"
                if reward_code:
                    result_msg += f"🎁 Code / الكود: `{reward_code}`\n\n"
                if not redirect_url and not reward_code:
                    result_msg += "✨ Approved but no link/code returned.\nتمت الموافقة ولكن لم يتم إرجاع رابط/كود.\n\n"
                result_msg += info_block
                await processing_msg.edit_text(result_msg)

            elif current_step == "error":
                result_msg = "❌ Verification failed / فشل التحقق\n\n"
                result_msg += info_block
                await processing_msg.edit_text(result_msg)

            else:
                # يشمل: pending، docUpload، collectStudentPersonalInfo، إلخ.
                if rejection_reasons:
                    header = "⚠️ Verification has rejection flags / يوجد أسباب رفض:\n\n"
                else:
                    header = "⏳ Verification in progress / التحقق جارٍ\n\n"

                result_msg = header + info_block
                result_msg += (
                    f"\n\n💡 Try again later / حاول لاحقاً:\n"
                    f"`/check {verification_id}`"
                )
                await processing_msg.edit_text(result_msg)

    except Exception as e:
        logger.error("Check verification failed: %s", e)
        await processing_msg.edit_text(
            f"❌ Error during query / خطأ أثناء الاستعلام: {str(e)}\n\n"
            "Please try again later or contact admin.\n"
            "يرجى المحاولة لاحقاً أو التواصل مع المسؤول."
        )


# الإبقاء على /getV4Code كاسم مستعار لتوافق الإصدارات السابقة
async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """معالجة الأمر /getV4Code - اسم مستعار للأمر /check (لتوافق الإصدارات السابقة)"""
    await check_command(update, context, db)
