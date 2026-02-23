"""وحدة مكافحة الكشف لطلبات واجهة برمجة تطبيقات SheerID.

توفر ترويسات شبيهة بالمتصفح، وتتبع NewRelic، وتزييف بصمة TLS
(عبر curl_cffi)، وبصمات ديناميكية، وتأخيرات شبيهة بالبشر،
وتهيئة الجلسات (warmup)، ودعم الوكلاء (proxy).
"""

import os
import random
import hashlib
import time
import uuid
import base64
import json
import logging

logger = logging.getLogger(__name__)

# ===================== التكوين (CONFIG) =====================
# وكيل (proxy) واحد أو وكلاء متعددون مفصولون بعلامة | (أنبوب)
# التنسيق: المضيف:المنفذ:المستخدم:كلمة_المرور  أو  http://المستخدم:كلمة_المرور@المضيف:المنفذ
# مثال: 1.2.3.4:6000:user:pass|5.6.7.8:7000:user:pass
PROXY_URL = os.environ.get("PROXY_URL", "")


def get_random_proxy() -> str | None:
    """اختيار وكيل عشوائي من PROXY_URL (يدعم وكلاء متعددين مفصولين بـ |)."""
    if not PROXY_URL:
        return None
    proxies = [p.strip() for p in PROXY_URL.split("|") if p.strip()]
    if not proxies:
        return None
    return random.choice(proxies)

# ===================== إصدارات كروم (CHROME VERSIONS) =====================
IMPERSONATE_OPTIONS = {
    "chrome": ["chrome131", "chrome130", "chrome124", "chrome120"],
    "edge": ["edge131", "edge127", "edge101"],
    "safari": ["safari18", "safari17_2_ios", "safari17_0"],
}
DEFAULT_IMPERSONATE = "chrome131"

# ===================== وكلاء المستخدم (USER AGENTS) =====================
USER_AGENTS = [
    # كروم 131
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # كروم 130
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    # كروم 131 نظام Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # إيدج 131
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
]

# ===================== المنصات (PLATFORMS sec-ch-ua) =====================
PLATFORMS = [
    ("Windows", '"Windows"', '"Chromium";v="131", "Google Chrome";v="131", "Not_A Brand";v="24"'),
    ("Windows", '"Windows"', '"Chromium";v="130", "Google Chrome";v="130", "Not_A Brand";v="24"'),
    ("macOS", '"macOS"', '"Chromium";v="131", "Google Chrome";v="131", "Not_A Brand";v="24"'),
    ("Linux", '"Linux"', '"Chromium";v="131", "Google Chrome";v="131", "Not_A Brand";v="24"'),
]

LANGUAGES = [
    "en-US,en;q=0.9",
    "en-US,en;q=0.9,es;q=0.8",
    "en-GB,en;q=0.9",
    "en-CA,en;q=0.9",
]

RESOLUTIONS = [
    "1920x1080", "1366x768", "1536x864", "1440x900",
    "1280x720", "2560x1440", "1600x900",
]


# ===================== البصمة (FINGERPRINT) =====================
def generate_fingerprint() -> str:
    """توليد تجزئة واقعية لبصمة المتصفح."""
    components = [
        str(int(time.time() * 1000)),
        str(random.random()),
        random.choice(RESOLUTIONS),
        str(random.choice([-8, -7, -6, -5, -4, 0, 1, 2])),
        random.choice(LANGUAGES).split(",")[0],
        random.choice(["Win32", "MacIntel", "Linux x86_64"]),
        random.choice(["Google Inc.", "Apple Computer, Inc.", ""]),
        str(random.randint(2, 16)),   # أنوية المعالج (CPU cores)
        str(random.randint(4, 32)),   # ذاكرة الجهاز (device memory)
        str(random.randint(0, 1)),    # دعم اللمس (touch support)
        str(uuid.uuid4()),
    ]
    return hashlib.md5("|".join(components).encode()).hexdigest()


# ===================== ترويسات NEWRELIC =====================
def _newrelic_headers() -> dict:
    """توليد ترويسات تتبع NewRelic المطلوبة بواسطة SheerID."""
    trace_id = uuid.uuid4().hex + uuid.uuid4().hex[:8]
    trace_id = trace_id[:32]
    span_id = uuid.uuid4().hex[:16]
    ts = int(time.time() * 1000)

    payload = {
        "v": [0, 1],
        "d": {
            "ty": "Browser",
            "ac": "364029",
            "ap": "134291347",
            "id": span_id,
            "tr": trace_id,
            "ti": ts,
        },
    }
    return {
        "newrelic": base64.b64encode(json.dumps(payload).encode()).decode(),
        "traceparent": f"00-{trace_id}-{span_id}-01",
        "tracestate": f"364029@nr=0-1-364029-134291347-{span_id}----{ts}",
    }


# ===================== الترويسات (HEADERS) =====================
def get_sheerid_headers() -> dict:
    """ترويسات كاملة شبيهة بالمتصفح لطلبات واجهة برمجة تطبيقات SheerID."""
    ua = random.choice(USER_AGENTS)
    platform = random.choice(PLATFORMS)
    lang = random.choice(LANGUAGES)
    nr = _newrelic_headers()

    return {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": lang,
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "content-type": "application/json",
        "sec-ch-ua": platform[2],
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": platform[1],
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua,
        "clientversion": "2.158.0",
        "clientname": "jslib",
        "origin": "https://services.sheerid.com",
        "referer": "https://services.sheerid.com/",
        **nr,
    }


# ===================== التأخيرات (DELAYS) =====================
def human_delay(min_ms: int = 300, max_ms: int = 1200):
    """تأخير بتوقيت شبيه بالبشر (توزيع جاما عندما يكون ذلك ممكناً)."""
    try:
        import numpy as np
        shape, scale = 2.0, (max_ms - min_ms) / 4000
        delay = min_ms / 1000 + np.random.gamma(shape, scale)
        delay = min(delay, max_ms / 1000)
    except ImportError:
        delay = random.randint(min_ms, max_ms) / 1000
        delay += random.uniform(0, 0.15)
    time.sleep(delay)


# ===================== الجلسة (SESSION) =====================
def _format_proxy(proxy: str) -> str | None:
    """تسوية تنسيقات الوكيل المختلفة إلى رابط URL يبدأ بـ http://..."""
    if not proxy:
        return None
    proxy = proxy.strip()
    if "://" in proxy:
        return proxy
    parts = proxy.split(":")
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    elif "@" in proxy:
        return f"http://{proxy}"
    return None


def create_session(proxy: str = None):
    """إنشاء جلسة HTTP بأفضل مكتبة متاحة.

    الأولوية: curl_cffi (تزييف TLS) > httpx > requests

    Args:
        proxy: تجاوز رابط الوكيل (Proxy URL). يتم الرجوع إلى متغير البيئة PROXY_URL في حالة عدم التحديد.

    Returns:
        مجموعة متصلة (tuple): (الجلسة، اسم_المكتبة)
    """
    proxy = _format_proxy(proxy or get_random_proxy())
    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy, "all://": proxy}
        logger.info(f"🔒 تم تكوين الوكيل: {proxy[:35]}...")

    imp = DEFAULT_IMPERSONATE

    # 1. جرب curl_cffi (الأفضل — بصمة TLS تتطابق مع متصفح كروم حقيقي)
    try:
        from curl_cffi import requests as curl_requests

        for ver in [imp, "chrome120", "chrome110", "chrome100"]:
            try:
                sess = (
                    curl_requests.Session(proxies=proxies, impersonate=ver)
                    if proxies
                    else curl_requests.Session(impersonate=ver)
                )
                logger.info(f"✅ مكافحة الكشف: مكتبة curl_cffi + انتحال TLS لإصدار {ver}")
                return sess, "curl_cffi"
            except Exception:
                continue

        # curl_cffi بدون انتحال شخصية (impersonation)
        sess = curl_requests.Session(proxies=proxies) if proxies else curl_requests.Session()
        logger.warning("⚠️  تم تحميل curl_cffi ولكن فشل انتحال TLS")
        return sess, "curl_cffi"

    except ImportError:
        logger.warning("❌ مكتبة curl_cffi غير مثبتة — يمكن كشف بصمة TLS!")
        logger.warning("   للتثبيت: pip install curl_cffi")

    # 2. مكتبة httpx (بصمة TLS قابلة للكشف لكنها عملية)
    try:
        import httpx
        proxy_url = proxies.get("all://") if proxies else None
        sess = httpx.Client(timeout=30, proxy=proxy_url)
        logger.info("⚠️  مكافحة الكشف: مكتبة httpx (بدون تزييف TLS)")
        return sess, "httpx"
    except ImportError:
        pass

    # 3. الرجوع إلى مكتبة requests (الأسوأ)
    import requests
    sess = requests.Session()
    if proxies:
        sess.proxies = proxies
    logger.warning("❌ مكافحة الكشف: مكتبة requests (خطر كشف عالي جداً)")
    return sess, "requests"


# ===================== التمهيد (WARMUP) =====================
def warm_session(session, program_id: str = None):
    """طلبات مسبقة لمحاكاة تحميل صفحة متصفح حقيقي."""
    base = "https://services.sheerid.com"
    hdrs = get_sheerid_headers()

    try:
        session.get(f"{base}/rest/v2/config", headers=hdrs, timeout=10)
        human_delay(500, 1000)
    except Exception:
        pass

    if program_id:
        try:
            session.get(f"{base}/rest/v2/program/{program_id}", headers=hdrs, timeout=10)
            human_delay(300, 700)
        except Exception:
            pass

    try:
        session.get(
            f"{base}/rest/v2/organization/search",
            params={"country": "US", "term": "", **({"programId": program_id} if program_id else {})},
            headers=hdrs,
            timeout=10,
        )
        human_delay(200, 500)
    except Exception:
        pass
