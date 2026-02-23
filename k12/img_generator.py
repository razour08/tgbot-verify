"""إنشاء مستند إثبات المعلم (PDF + PNG)"""
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

from xhtml2pdf import pisa


def _render_template(first_name: str, last_name: str) -> str:
    """قراءة القالب واستبدال الاسم/الرقم الوظيفي/التاريخ، وتطبيق متغيرات CSS."""
    full_name = f"{first_name} {last_name}"
    employee_id = random.randint(1000000, 9999999)
    current_date = datetime.now().strftime("%m/%d/%Y %I:%M %p")

    template_path = Path(__file__).parent / "card-temp.html"
    html = template_path.read_text(encoding="utf-8")

    # تطبيق متغيرات CSS لتتوافق مع xhtml2pdf
    color_map = {
        "var(--primary-blue)": "#0056b3",
        "var(--border-gray)": "#dee2e6",
        "var(--bg-gray)": "#f8f9fa",
    }
    for placeholder, color in color_map.items():
        html = html.replace(placeholder, color)

    # استبدال الاسم التجريبي / الرقم الوظيفي / التاريخ (يظهر الاسم + span في مكانين داخل القالب)
    html = html.replace("Sarah J. Connor", full_name)
    html = html.replace("E-9928104", f"E-{employee_id}")
    html = html.replace('id="currentDate"></span>', f'id="currentDate">{current_date}</span>')

    return html


def generate_teacher_pdf(first_name: str, last_name: str) -> bytes:
    """إنشاء مستند إثبات المعلم بصيغة PDF كبايتات (bytes)."""
    html = _render_template(first_name, last_name)

    output = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=output, encoding="utf-8")
    if pisa_status.err:
        raise Exception("فشل إنشاء ملف PDF")

    pdf_data = output.getvalue()
    output.close()
    return pdf_data


def generate_teacher_png(first_name: str, last_name: str) -> bytes:
    """استخدام Playwright لالتقاط الشاشة وإنشاء صورة PNG (يتطلب تثبيت playwright + chromium)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "نسخة Playwright مطلوبة، يرجى تنفيذ `pip install playwright` ثم `playwright install chromium`"
        ) from exc

    html = _render_template(first_name, last_name)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 1000})
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(500)  # انتظار ثبات التنسيق والتصميم
        card = page.locator(".browser-mockup")
        png_bytes = card.screenshot(type="png")
        browser.close()

    return png_bytes


# التوافق مع الاستدعاء القديم: إنشاء PDF افتراضيًا
def generate_teacher_image(first_name: str, last_name: str) -> bytes:
    return generate_teacher_pdf(first_name, last_name)
