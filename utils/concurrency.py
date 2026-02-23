"""أداة التحكم في التزامن (النسخة المحسنة)

تحسينات الأداء:
1. حدود تزامن ديناميكية (بناءً على حمل النظام).
2. فصل التحكم في التزامن الخاص بكل نوع من أنواع التحقق.
3. دعم عدد أكبر من المهام المتزامنة.
4. مراقبة الحمل والضبط التلقائي.
"""
import asyncio
import logging
from typing import Dict
import psutil

logger = logging.getLogger(__name__)

# حساب الحد الأقصى للتزامن ديناميكياً
def _calculate_max_concurrency() -> int:
    """حساب الحد الأقصى المسموح به للتزامن بناءً على موارد النظام"""
    try:
        cpu_count = psutil.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # الحساب بناءً على الذاكرة ووحدة المعالجة المركزية (CPU)
        # كل نواة CPU تدعم 3-5 مهام متزامنة
        # كل جيجابايت من الذاكرة يدعم مهمتين متزامنتين
        cpu_based = cpu_count * 4
        memory_based = int(memory_gb * 2)
        
        # أخذ القيمة الأصغر بينهما، وتحديد حد أدنى وأقصى
        max_concurrent = min(cpu_based, memory_based)
        max_concurrent = max(10, min(max_concurrent, 100))  # بين 10 و 100
        
        logger.info(
            f"موارد النظام: CPU={cpu_count}, Memory={memory_gb:.1f}GB, "
            f"التزامن المحسوب={max_concurrent}"
        )
        
        return max_concurrent
        
    except Exception as e:
        logger.warning(f"تعذر الحصول على معلومات موارد النظام: {e}, استخدام القيمة الافتراضية")
        return 20  # القيمة الافتراضية

# حساب حد التزامن لكل نوع من أنواع التحقق
_base_concurrency = _calculate_max_concurrency()

# إنشاء إشارات دخول (semaphores) مستقلة للأنواع المختلفة من عمليات التحقق
# وذلك لتجنب حظر نوع ما للأنواع الأخرى
_verification_semaphores: Dict[str, asyncio.Semaphore] = {
    "gemini_one_pro": asyncio.Semaphore(_base_concurrency // 5),
    "chatgpt_teacher_k12": asyncio.Semaphore(_base_concurrency // 5),
    "spotify_student": asyncio.Semaphore(_base_concurrency // 5),
    "youtube_student": asyncio.Semaphore(_base_concurrency // 5),
    "bolt_teacher": asyncio.Semaphore(_base_concurrency // 5),
}


def get_verification_semaphore(verification_type: str) -> asyncio.Semaphore:
    """الحصول على إشارة الدخول (semaphore) لنوع التحقق المحدّد
    
    Args:
        verification_type: نوع التحقق
        
    Returns:
        asyncio.Semaphore: إشارة الدخول (semaphore) المقابلة
    """
    semaphore = _verification_semaphores.get(verification_type)
    
    if semaphore is None:
        # نوع غير معروف، قم بإنشاء إشارة دخول (semaphore) افتراضية
        semaphore = asyncio.Semaphore(_base_concurrency // 3)
        _verification_semaphores[verification_type] = semaphore
        logger.info(
            f"إنشاء إشارة دخول (semaphore) لنوع التحقق الجديد {verification_type}: "
            f"الحد={_base_concurrency // 3}"
        )
    
    return semaphore


def get_concurrency_stats() -> Dict[str, Dict[str, int]]:
    """الحصول على إحصائيات التزامن
    
    Returns:
        dict: معلومات التزامن لكل نوع تحقق
    """
    stats = {}
    for vtype, semaphore in _verification_semaphores.items():
        # ملاحظة: السمة _value سمة داخلية (internal) وقد تتغير بين إصدارات بايثون المختلفة
        try:
            available = semaphore._value if hasattr(semaphore, '_value') else 0
            limit = _base_concurrency // 3
            in_use = limit - available
        except Exception:
            available = 0
            limit = _base_concurrency // 3
            in_use = 0
        
        stats[vtype] = {
            'limit': limit,
            'in_use': in_use,
            'available': available,
        }
    
    return stats


async def monitor_system_load() -> Dict[str, float]:
    """مراقبة حمل النظام
    
    Returns:
        dict: معلومات حمل النظام
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'concurrency_limit': _base_concurrency,
        }
    except Exception as e:
        logger.error(f"فشل مراقبة حمل النظام: {e}")
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'concurrency_limit': _base_concurrency,
        }


def adjust_concurrency_limits(multiplier: float = 1.0):
    """تعديل حدود التزامن ديناميكياً
    
    Args:
        multiplier: مُعامِل الضبط (0.5 - 2.0)
    """
    global _verification_semaphores, _base_concurrency
    
    # تحديد نطاق المُعامل (multiplier)
    multiplier = max(0.5, min(multiplier, 2.0))
    
    new_base = int(_base_concurrency * multiplier)
    new_limit = max(5, min(new_base // 3, 50))  # 5 إلى 50 لكل نوع
    
    logger.info(
        f"ضبط حدود التزامن: المُعامل={multiplier}, "
        f"القيمة_الأساسية_الجديدة={new_base}, لكل_نوع={new_limit}"
    )
    
    # إنشاء إشارات دخول (semaphores) جديدة
    for vtype in _verification_semaphores.keys():
        _verification_semaphores[vtype] = asyncio.Semaphore(new_limit)


# مهمة مراقبة الحمل
_monitor_task = None

async def start_load_monitoring(interval: float = 60.0):
    """بدء مهمة مراقبة الحمل
    
    Args:
        interval: الفاصل الزمني للمراقبة (بالثواني)
    """
    global _monitor_task
    
    if _monitor_task is not None:
        return
    
    async def monitor_loop():
        while True:
            try:
                await asyncio.sleep(interval)
                
                load_info = await monitor_system_load()
                cpu = load_info['cpu_percent']
                memory = load_info['memory_percent']
                
                logger.info(
                    f"حمل النظام: CPU={cpu:.1f}%, الذاكرة={memory:.1f}%"
                )
                
                # ضبط حدود التزامن تلقائياً
                if cpu > 80 or memory > 85:
                    # الحمل مرتفع جداً، يتم خفض التزامن
                    adjust_concurrency_limits(0.7)
                    logger.warning("حمل النظام مرتفع جداً، جاري خفض حدود التزامن")
                elif cpu < 40 and memory < 60:
                    # الحمل منخفض، يمكن زيادة التزامن
                    adjust_concurrency_limits(1.2)
                    logger.info("حمل النظام منخفض، جاري زيادة حدود التزامن")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"استثناء في مراقبة الحمل: {e}")
    
    _monitor_task = asyncio.create_task(monitor_loop())
    logger.info(f"تم بدء مراقبة الحمل: interval={interval}s")


async def stop_load_monitoring():
    """إيقاف مهمة مراقبة الحمل"""
    global _monitor_task
    
    if _monitor_task is not None:
        _monitor_task.cancel()
        try:
            await _monitor_task
        except asyncio.CancelledError:
            pass
        _monitor_task = None
        logger.info("تم إيقاف مراقبة الحمل")
