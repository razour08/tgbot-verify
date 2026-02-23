"""مولد مستندات الطالب بصيغة PNG - نظام LionPATH لجامعة ولاية بنسلفانيا (مكافحة الاحتيال، مستندات متعددة)"""
import random
import string
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance


def _postprocess_image(png_bytes: bytes) -> bytes:
    """معالجة لقطة الشاشة لتبدو وكأنها صورة/مسح ضوئي حقيقي.

    يطبق: دوران طفيف، ضوضاء غاوسي، ضبابية خفيفة،
    تغيير السطوع/التباين، تشوهات ضغط JPEG،
    وهوامش قص عشوائية.
    """
    img = Image.open(BytesIO(png_bytes)).convert('RGB')

    # 1. دوران عشوائي طفيف (يحاكي صورة غير محاذية)
    angle = random.uniform(-1.2, 1.2)
    if abs(angle) > 0.3:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))

    # 2. هوامش قص عشوائية (يحاكي تأطير غير مثالي)
    w, h = img.size
    crop_left = random.randint(0, 8)
    crop_top = random.randint(0, 8)
    crop_right = random.randint(0, 8)
    crop_bottom = random.randint(0, 8)
    img = img.crop((crop_left, crop_top, w - crop_right, h - crop_bottom))

    # 3. إضافة ضوضاء غاوسي (يحاكي ضوضاء مستشعر الكاميرا)
    arr = np.array(img, dtype=np.float32)
    noise_strength = random.uniform(1.5, 4.0)
    noise = np.random.normal(0, noise_strength, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # 4. ضبابية غاوسية خفيفة (يحاكي عدم تركيز الكاميرا الطفيف)
    blur_radius = random.uniform(0.2, 0.6)
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # 5. تغيير عشوائي للسطوع والتباين
    brightness_factor = random.uniform(0.95, 1.05)
    img = ImageEnhance.Brightness(img).enhance(brightness_factor)

    contrast_factor = random.uniform(0.95, 1.05)
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)

    # 6. تشوهات ضغط JPEG ثم العودة إلى PNG
    # (يحاكي صورة محفوظة/مشاركة عبر تطبيقات المراسلة)
    jpeg_quality = random.randint(82, 92)
    jpeg_buf = BytesIO()
    img.save(jpeg_buf, format='JPEG', quality=jpeg_quality)
    jpeg_buf.seek(0)
    img = Image.open(jpeg_buf)

    # 7. التصدير النهائي بصيغة PNG
    out_buf = BytesIO()
    img.save(out_buf, format='PNG')
    return out_buf.getvalue()


def generate_psu_id():
    """توليد معرف PSU عشوائي (9 أرقام)"""
    return f"9{random.randint(10000000, 99999999)}"


def generate_psu_email(first_name, last_name):
    """توليد بريد PSU: الاسم_الأول.الاسم_الأخير + 3-4 أرقام @psu.edu"""
    digit_count = random.choice([3, 4])
    digits = ''.join([str(random.randint(0, 9)) for _ in range(digit_count)])
    email = f"{first_name.lower()}.{last_name.lower()}{digits}@psu.edu"
    return email


def _random_filename(prefix):
    """توليد اسم ملف عشوائي مثل 'schedule_a8f2.png'"""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{suffix}.png"


# ============================================================
# بيانات المقررات الدراسية العشوائية
# ============================================================

COURSES_POOL = [
    ("CMPSC 121", "Introduction to Programming", "3.00"),
    ("CMPSC 122", "Intermediate Programming", "3.00"),
    ("CMPSC 131", "Programming and Computation I", "3.00"),
    ("CMPSC 132", "Programming and Computation II", "3.00"),
    ("CMPSC 221", "Object-Oriented Programming with Web", "3.00"),
    ("CMPSC 360", "Discrete Mathematics for CS", "3.00"),
    ("CMPSC 431W", "Database Management Systems", "3.00"),
    ("CMPSC 461", "Programming Language Concepts", "3.00"),
    ("CMPSC 465", "Data Structures and Algorithms", "3.00"),
    ("CMPSC 473", "Operating Systems Design", "3.00"),
    ("CMPSC 474", "Server-Side Web Development", "3.00"),
    ("CMPSC 483W", "Software Engineering Capstone", "3.00"),
    ("MATH 140", "Calculus With Analytic Geometry I", "4.00"),
    ("MATH 141", "Calculus With Analytic Geometry II", "4.00"),
    ("MATH 220", "Matrices", "2.00"),
    ("MATH 230", "Calculus and Vector Analysis", "4.00"),
    ("MATH 231", "Calculus of Several Variables", "2.00"),
    ("MATH 251", "Ordinary and Partial Differential Equations", "4.00"),
    ("MATH 311W", "Concepts of Discrete Mathematics", "3.00"),
    ("STAT 200", "Elementary Statistics", "4.00"),
    ("STAT 318", "Elementary Probability", "3.00"),
    ("STAT 414", "Introduction to Probability Theory", "3.00"),
    ("PHYS 211", "General Physics: Mechanics", "4.00"),
    ("PHYS 212", "General Physics: Electricity and Magnetism", "4.00"),
    ("PHYS 213", "Foundations of Physics III", "2.00"),
    ("ENGL 015", "Rhetoric and Composition", "3.00"),
    ("ENGL 202C", "Technical Writing", "3.00"),
    ("ENGL 030", "Heritage of Western Literature", "3.00"),
    ("ECON 102", "Introductory Microeconomic Analysis", "3.00"),
    ("ECON 104", "Introductory Macroeconomic Analysis", "3.00"),
    ("IST 110", "Information, People, and Technology", "3.00"),
    ("IST 210", "Organization of Data", "3.00"),
    ("IST 261", "Application Development Design", "3.00"),
    ("IST 311", "Object-Oriented Design and Software Applications", "3.00"),
    ("PSYCH 100", "Introductory Psychology", "3.00"),
    ("COMM 150", "Effective Speech", "3.00"),
    ("BIOL 110", "Biology: Basic Concepts and Biodiversity", "4.00"),
    ("CHEM 110", "Chemical Principles I", "3.00"),
    ("SOC 119", "Introduction to Sociology", "3.00"),
    ("HIST 020", "American Civilization to 1877", "3.00"),
    ("PHIL 103", "Introduction to Ethics", "3.00"),
    ("ACCTG 211", "Financial and Managerial Accounting", "4.00"),
    ("MGMT 301", "Basic Management Concepts", "3.00"),
    ("MKTG 301", "Principles of Marketing", "3.00"),
    ("FIN 301", "Corporation Finance", "3.00"),
    ("EE 210", "Circuits and Devices", "4.00"),
    ("ME 201", "Introduction to Thermodynamics", "3.00"),
    ("KINES 084", "Concepts of Fitness and Wellness", "3.00"),
]

ROOMS_POOL = [
    ("Willard", ["062", "119", "203", "315"]),
    ("Thomas", ["102", "201", "310", "117"]),
    ("Westgate", ["E101", "E201", "W103", "W210"]),
    ("Boucke", ["210", "304", "106", "225"]),
    ("Osmond", ["112", "215", "101", "306"]),
    ("Hammond", ["100", "218", "312", "114"]),
    ("Deike", ["115", "207", "308", "104"]),
    ("Sackett", ["201", "302", "110", "204"]),
    ("Sparks", ["101", "203", "315", "106"]),
    ("Rackley", ["102", "204", "301", "105"]),
    ("IST", ["120", "220", "325", "118"]),
    ("Smeal", ["106", "210", "314", "100"]),
    ("Forum", ["101", "207", "301", "114"]),
    ("Kern", ["103", "212", "314", "107"]),
    ("Wartik", ["100", "111", "222", "300"]),
    ("Mueller", ["103", "204", "301", "105"]),
    ("Henderson", ["101", "204", "308", "112"]),
    ("Leonhard", ["100", "203", "307", "115"]),
]

TIME_SLOTS = [
    "MoWeFr 8:00AM - 8:50AM",
    "MoWeFr 9:05AM - 9:55AM",
    "MoWeFr 10:10AM - 11:00AM",
    "MoWeFr 11:15AM - 12:05PM",
    "MoWeFr 1:25PM - 2:15PM",
    "MoWeFr 2:30PM - 3:20PM",
    "MoWeFr 3:35PM - 4:25PM",
    "TuTh 8:00AM - 9:15AM",
    "TuTh 9:05AM - 10:20AM",
    "TuTh 10:35AM - 11:50AM",
    "TuTh 12:05PM - 1:20PM",
    "TuTh 1:35PM - 2:50PM",
    "TuTh 2:30PM - 3:45PM",
    "TuTh 4:00PM - 5:15PM",
    "Mo 6:00PM - 8:50PM",
    "Tu 6:00PM - 8:50PM",
    "We 6:00PM - 8:50PM",
    "Th 6:00PM - 8:50PM",
]

MAJORS = [
    "Computer Science (BS)",
    "Software Engineering (BS)",
    "Information Sciences and Technology (BS)",
    "Data Science (BS)",
    "Electrical Engineering (BS)",
    "Mechanical Engineering (BS)",
    "Business Administration (BS)",
    "Psychology (BA)",
    "Biology (BS)",
    "Chemistry (BS)",
    "Mathematics (BS)",
    "Economics (BA)",
    "Communications (BA)",
    "Accounting (BS)",
    "Finance (BS)",
    "Marketing (BS)",
    "Civil Engineering (BS)",
    "Aerospace Engineering (BS)",
]

INSTRUCTORS = [
    "Dr. J. Anderson", "Dr. M. Chen", "Dr. S. Patel", "Dr. R. Williams",
    "Dr. K. Johnson", "Dr. L. Martinez", "Dr. A. Thompson", "Dr. D. Miller",
    "Prof. T. Davis", "Prof. N. Wilson", "Prof. E. Brown", "Prof. C. Taylor",
    "Dr. H. Garcia", "Dr. B. Robinson", "Prof. W. Clark", "Dr. P. Lewis",
    "Dr. F. Walker", "Prof. G. Hall", "Dr. V. Young", "Prof. I. Allen",
]

ENROLLMENT_STATUSES = [
    ("✓ Enrolled", "#e6fffa", "#007a5e", "#b2f5ea"),
    ("✓ Registered", "#e8f5e9", "#2e7d32", "#a5d6a7"),
    ("✓ Active", "#e3f2fd", "#1565c0", "#90caf9"),
]

ACADEMIC_STANDINGS = [
    "Good Standing", "Dean's List", "Good Standing",
    "Good Standing", "Good Standing", "Dean's List",
]


def _get_current_semester():
    """إرجاع سلسلة نصية للفصل الدراسي الحالي بناءً على تاريخ اليوم."""
    now = datetime.now()
    month = now.month
    year = now.year

    if month >= 8:
        return f"Fall {year}", f"Aug {random.randint(19,26)} - Dec {random.randint(10,16)}"
    elif month >= 5:
        return f"Summer {year}", f"May {random.randint(11,15)} - Aug {random.randint(6,10)}"
    else:
        return f"Spring {year}", f"Jan {random.randint(11,15)} - May {random.randint(1,5)}"


def _generate_random_schedule():
    """توليد 4-5 مقررات عشوائية بأوقات وغرف فريدة."""
    num_courses = random.choice([4, 5])
    courses = random.sample(COURSES_POOL, num_courses)
    times = random.sample(TIME_SLOTS, num_courses)

    schedule = []
    for i, (code, title, units) in enumerate(courses):
        building = random.choice(ROOMS_POOL)
        room = f"{building[0]} {random.choice(building[1])}"
        class_nbr = str(random.randint(10000, 29999))
        instructor = random.choice(INSTRUCTORS) if random.random() < 0.7 else None
        schedule.append({
            "class_nbr": class_nbr,
            "code": code,
            "title": title,
            "time": times[i],
            "room": room,
            "units": units,
            "instructor": instructor,
        })

    return schedule


def _random_retrieve_time():
    """توليد طابع زمني (بيانات مسترجعة) عشوائي قليلاً."""
    now = datetime.now()
    offset = timedelta(minutes=random.randint(0, 45), seconds=random.randint(0, 59))
    t = now - offset
    return t.strftime('%m/%d/%Y, %I:%M:%S %p')


def generate_schedule_html(first_name, last_name, school_id='2565'):
    """توليد HTML لجدول LionPATH لجامعة ولاية بنسلفانيا مع توزيع مرئي عشوائي."""
    psu_id = generate_psu_id()
    name = f"{first_name} {last_name}"
    date = _random_retrieve_time()
    major = random.choice(MAJORS)
    semester, semester_range = _get_current_semester()
    schedule = _generate_random_schedule()
    standing = random.choice(ACADEMIC_STANDINGS)
    status_text, status_bg, status_color, status_border = random.choice(ENROLLMENT_STATUSES)

    # توزيع مرئي عشوائي
    bg_gray = f"#{random.randint(227,232):02x}{random.randint(227,232):02x}{random.randint(227,232):02x}"
    content_bg = f"#{random.randint(252,255):02x}{random.randint(252,255):02x}{random.randint(252,255):02x}"
    body_font_size = random.choice(["12.5px", "13px", "13.5px"])
    show_instructor = random.choice([True, False])
    show_standing = random.choice([True, False])

    # عناصر التنقل تختلف قليلاً
    nav_extras = random.choice([
        '<div class="nav-item">Campus Life</div>',
        '<div class="nav-item">Services</div>',
        '<div class="nav-item">Campus Life</div><div class="nav-item">Resources</div>',
    ])

    # بناء صفوف المقررات
    course_rows = ""
    for c in schedule:
        instructor_col = f'<td>{c["instructor"]}</td>' if (show_instructor and c["instructor"]) else (f'<td>—</td>' if show_instructor else '')
        course_rows += f"""
                <tr>
                    <td>{c['class_nbr']}</td>
                    <td class="course-code">{c['code']}</td>
                    <td class="course-title">{c['title']}</td>
                    <td>{c['time']}</td>
                    <td>{c['room']}</td>
                    {instructor_col}
                    <td>{c['units']}</td>
                </tr>"""

    total_units = sum(float(c['units']) for c in schedule)
    current_year = datetime.now().year
    instructor_th = '<th width="12%">Instructor</th>' if show_instructor else ''
    title_width = "30%" if show_instructor else "35%"

    # صف الموقف الأكاديمي
    standing_html = ""
    if show_standing:
        standing_html = f"""
            <div>
                <div class="info-label">Academic Standing</div>
                <div class="info-val">{standing}</div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LionPATH - Student Home</title>
    <style>
        :root {{
            --psu-blue: #1E407C;
            --psu-light-blue: #96BEE6;
            --bg-gray: {bg_gray};
            --text-color: #333;
        }}

        body {{
            font-family: "Roboto", "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: {bg_gray};
            margin: 0;
            padding: {random.randint(18,24)}px;
            color: var(--text-color);
            display: flex;
            justify-content: center;
        }}

        .viewport {{
            width: 100%;
            max-width: {random.randint(1080, 1120)}px;
            background-color: #fff;
            box-shadow: 0 {random.randint(4,6)}px {random.randint(18,22)}px rgba(0,0,0,{random.uniform(0.12, 0.18):.2f});
            min-height: 800px;
            display: flex;
            flex-direction: column;
        }}

        .header {{
            background-color: var(--psu-blue);
            color: white;
            padding: 0 20px;
            height: {random.randint(56,64)}px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .psu-logo {{
            font-family: "Georgia", serif;
            font-size: {random.randint(19,21)}px;
            font-weight: bold;
            letter-spacing: 1px;
            border-right: 1px solid rgba(255,255,255,0.3);
            padding-right: 15px;
        }}

        .system-name {{
            font-size: {random.randint(17,19)}px;
            font-weight: 300;
        }}

        .user-menu {{
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .nav-bar {{
            background-color: #f8f8f8;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
            font-size: {body_font_size};
            color: #666;
            display: flex;
            gap: 20px;
        }}
        .nav-item {{ cursor: pointer; }}
        .nav-item.active {{ color: var(--psu-blue); font-weight: bold; border-bottom: 2px solid var(--psu-blue); padding-bottom: 8px; }}

        .content {{
            padding: {random.randint(25,35)}px;
            flex: 1;
        }}

        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}

        .page-title {{
            font-size: {random.randint(22,26)}px;
            color: var(--psu-blue);
            margin: 0;
        }}

        .term-selector {{
            background: #fff;
            border: 1px solid #ccc;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
            color: #333;
            font-weight: bold;
        }}

        .student-card {{
            background: {content_bg};
            border: 1px solid #e0e0e0;
            padding: 15px;
            margin-bottom: 25px;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            font-size: {body_font_size};
        }}
        .info-label {{ color: #777; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; }}
        .info-val {{ font-weight: bold; color: #333; font-size: 14px; }}
        .status-badge {{
            background-color: {status_bg}; color: {status_color};
            padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 1px solid {status_border};
        }}

        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: {body_font_size};
        }}

        .schedule-table th {{
            text-align: left;
            padding: 12px;
            background-color: #f0f0f0;
            border-bottom: 2px solid #ccc;
            color: #555;
        }}

        .schedule-table td {{
            padding: {random.randint(13,17)}px 12px;
            border-bottom: 1px solid #eee;
        }}

        .course-code {{ font-weight: bold; color: var(--psu-blue); }}
        .course-title {{ font-weight: 500; }}

        .total-row {{
            font-weight: bold;
            background-color: #f8f8f8;
        }}

        @media print {{
            body {{ background: white; padding: 0; }}
            .viewport {{ box-shadow: none; max-width: 100%; min-height: auto; }}
            .nav-bar {{ display: none; }}
            @page {{ margin: 1cm; size: landscape; }}
        }}
    </style>
</head>
<body>

<div class="viewport">
    <div class="header">
        <div class="brand">
            <div class="psu-logo">PennState</div>
            <div class="system-name">LionPATH</div>
        </div>
        <div class="user-menu">
            <span>Welcome, <strong>{name}</strong></span>
            <span>|</span>
            <span>Sign Out</span>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item">Student Home</div>
        <div class="nav-item active">My Class Schedule</div>
        <div class="nav-item">Academics</div>
        <div class="nav-item">Finances</div>
        {nav_extras}
    </div>

    <div class="content">
        <div class="page-header">
            <h1 class="page-title">My Class Schedule</h1>
            <div class="term-selector">
                Term: <strong>{semester}</strong> ({semester_range})
            </div>
        </div>

        <div class="student-card">
            <div>
                <div class="info-label">Student Name</div>
                <div class="info-val">{name}</div>
            </div>
            <div>
                <div class="info-label">PSU ID</div>
                <div class="info-val">{psu_id}</div>
            </div>
            <div>
                <div class="info-label">Academic Program</div>
                <div class="info-val">{major}</div>
            </div>
            <div>
                <div class="info-label">Enrollment Status</div>
                <div class="status-badge">{status_text}</div>
            </div>{standing_html}
        </div>

        <div style="margin-bottom: 10px; font-size: 12px; color: #666; text-align: right;">
            Data retrieved: <span>{date}</span>
        </div>

        <table class="schedule-table">
            <thead>
                <tr>
                    <th width="10%">Class Nbr</th>
                    <th width="12%">Course</th>
                    <th width="{title_width}">Title</th>
                    <th width="20%">Days &amp; Times</th>
                    <th width="10%">Room</th>
                    {instructor_th}
                    <th width="8%">Units</th>
                </tr>
            </thead>
            <tbody>{course_rows}
                <tr class="total-row">
                    <td colspan="{'6' if show_instructor else '5'}" style="text-align: right;">Total Units:</td>
                    <td>{total_units:.2f}</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top: {random.randint(40,60)}px; border-top: 1px solid #ddd; padding-top: 10px; font-size: 11px; color: #888; text-align: center;">
            &copy; {current_year} The Pennsylvania State University. All rights reserved.<br>
            LionPATH is the student information system for Penn State.
        </div>
    </div>
</div>

</body>
</html>
"""
    return html


def generate_enrollment_letter_html(first_name, last_name, psu_id, major):
    """توليد HTML لرسالة التحقق من التسجيل الرسمية لـ PSU."""
    name = f"{first_name} {last_name}"
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    semester, _ = _get_current_semester()
    standing = random.choice(ACADEMIC_STANDINGS)

    # تفاصيل تسجيل عشوائية
    credits_earned = random.randint(24, 95)
    credits_attempted = credits_earned + random.randint(0, 6)
    gpa = round(random.uniform(2.8, 3.95), 2)
    expected_grad_year = now.year + random.randint(1, 3)
    expected_grad_month = random.choice(["May", "December"])
    enroll_year = now.year - random.randint(1, 4)
    enroll_month = random.choice(["August", "January"])
    report_id = f"LPR-{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PSU Enrollment Verification</title>
    <style>
        body {{
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}

        .page {{
            width: 8.5in;
            min-height: 11in;
            background: white;
            padding: 1in;
            box-sizing: border-box;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            color: #333;
            position: relative;
        }}

        .header {{
            margin-bottom: 40px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 20px;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}

        .psu-logo-mark {{
            width: 50px;
            height: 50px;
            background-color: #1E407C;
            mask: url('data:image/svg+xml;utf8,<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="45"/></svg>');
            -webkit-mask: url('data:image/svg+xml;utf8,<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="45"/></svg>');
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 28px;
            font-family: serif;
            margin-right: 15px;
        }}

        .org-name {{
            font-size: 18px;
            font-weight: bold;
            color: #1E407C;
            text-transform: uppercase;
        }}

        .reg-address {{
            font-size: 11px;
            color: #666;
            line-height: 1.4;
            text-align: right;
            position: absolute;
            top: 1in;
            right: 1in;
        }}

        .content {{
            font-size: 11pt;
            line-height: 1.6;
        }}

        .title {{
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            margin: 30px 0;
            text-transform: uppercase;
            text-decoration: underline;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            font-size: 11pt;
        }}

        .data-table td {{
            padding: 8px 5px;
            border-bottom: 1px solid #eee;
        }}

        .data-label {{
            font-weight: bold;
            width: 40%;
            color: #555;
        }}

        .data-value {{
            font-weight: 600;
            color: #000;
        }}

        .footer {{
            position: absolute;
            bottom: 0.75in;
            left: 1in;
            right: 1in;
            font-size: 9px;
            color: #888;
            text-align: center;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }}

        @media print {{
            body {{ background: white; padding: 0; }}
            .page {{ box-shadow: none; margin: 0; width: 100%; height: auto; }}
        }}
    </style>
</head>
<body>

<div class="page">
    <div class="header">
        <div class="logo-area">
            <div class="psu-logo-mark">P</div>
            <div class="org-name">The Pennsylvania State University</div>
        </div>
        <div class="reg-address">
            <strong>Office of the University Registrar</strong><br>
            112 Shields Building<br>
            University Park, PA 16802<br>
            Phone: (814) 865-6357
        </div>
    </div>

    <div class="content">
        <div style="margin-bottom: 20px;">{date_str}</div>

        <div style="margin-bottom: 20px;">
            <strong>To Whom It May Concern:</strong>
        </div>

        <p>
            This letter is to verify the enrollment status of the student listed below
            at The Pennsylvania State University. This information is generated from the
            University's official student information system (LionPATH).
        </p>

        <div class="title">Enrollment Verification</div>

        <table class="data-table">
            <tr>
                <td class="data-label">Student Name:</td>
                <td class="data-value">{name}</td>
            </tr>
            <tr>
                <td class="data-label">Penn State ID:</td>
                <td class="data-value">{psu_id}</td>
            </tr>
            <tr>
                <td class="data-label">Academic Program:</td>
                <td class="data-value">{major}</td>
            </tr>
            <tr>
                <td class="data-label">Current Term:</td>
                <td class="data-value">{semester}</td>
            </tr>
            <tr>
                <td class="data-label">Enrollment Status:</td>
                <td class="data-value" style="color: green;">Full-Time, Active</td>
            </tr>
            <tr>
                <td class="data-label">Academic Standing:</td>
                <td class="data-value">{standing}</td>
            </tr>
            <tr>
                <td class="data-label">Credits Earned:</td>
                <td class="data-value">{credits_earned}</td>
            </tr>
            <tr>
                <td class="data-label">Credits Attempted:</td>
                <td class="data-value">{credits_attempted}</td>
            </tr>
            <tr>
                <td class="data-label">Cumulative GPA:</td>
                <td class="data-value">{gpa:.2f}</td>
            </tr>
            <tr>
                <td class="data-label">Initial Enrollment:</td>
                <td class="data-value">{enroll_month} {enroll_year}</td>
            </tr>
            <tr>
                <td class="data-label">Expected Graduation:</td>
                <td class="data-value">{expected_grad_month} {expected_grad_year}</td>
            </tr>
        </table>

        <p>
            The student listed above is currently enrolled and in {standing.lower()} at Penn State.
            Should you require further information, authorized requests may be submitted
            to the Office of the University Registrar.
        </p>

        <div style="margin-top: 50px;">
            Sincerely,
        </div>
        <div style="margin-top: 10px;">
            <strong>Office of the University Registrar</strong><br>
            The Pennsylvania State University
        </div>
    </div>

    <div class="footer">
        Generated by LionPATH for The Pennsylvania State University | Report ID: {report_id} | {date_str}<br>
        This document is valid for 90 days from the date of issuance.
    </div>
</div>

</body>
</html>
"""
    return html


# دالة الصورة المفردة القديمة (متوافقة مع الإصدارات السابقة)
def generate_html(first_name, last_name, school_id='2565'):
    """توليد HTML لـ LionPATH لجامعة ولاية بنسلفانيا (غلاف قديم)."""
    return generate_schedule_html(first_name, last_name, school_id)


def _html_to_png(html_content, width=1200, height=None):
    """تحويل HTML إلى PNG باستخدام منفذ عرض (viewport) عشوائي ودقة شاشة Retina."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                ]
            )
            context = browser.new_context(
                viewport={'width': width, 'height': height or 900},
                device_scale_factor=2,
            )
            page = context.new_page()

            page.set_content(html_content, wait_until='domcontentloaded')
            page.wait_for_load_state('load', timeout=5000)

            # حساب الارتفاع تلقائياً إذا لم يتم تحديده
            if height is None:
                actual_h = page.evaluate(
                    "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                )
                page.set_viewport_size({'width': width, 'height': actual_h})

            # إزاحة تمرير عشوائية طفيفة لكسر البصمة المطابقة للبيكسل
            scroll_y = random.randint(0, 3)
            if scroll_y > 0:
                page.evaluate(f"window.scrollTo(0, {scroll_y})")
                page.wait_for_timeout(100)

            screenshot_bytes = page.screenshot(type='png', full_page=True)
            browser.close()

        # المعالجة البعدية لمحاكاة صورة حقيقية
        return _postprocess_image(screenshot_bytes)

    except ImportError:
        raise Exception("Playwright required: pip install playwright && playwright install chromium")
    except Exception as e:
        raise Exception(f"Image generation failed: {str(e)}")


def generate_image(first_name, last_name, school_id='2565'):
    """توليد لقطة شاشة واحدة لـ LionPATH بصيغة PNG (قديمة)."""
    html_content = generate_schedule_html(first_name, last_name, school_id)
    width = random.randint(1180, 1280)
    return _html_to_png(html_content, width=width)


def generate_images(first_name, last_name, school_id='2565'):
    """توليد مستندين: لقطة شاشة للجدول + رسالة التسجيل.

    Returns:
        قائمة بالقواميس (list[dict]): [{"file_name": str, "data": bytes}, ...]
    """
    psu_id = generate_psu_id()
    major = random.choice(MAJORS)

    schedule_html = generate_schedule_html(first_name, last_name, school_id)
    letter_html = generate_enrollment_letter_html(first_name, last_name, psu_id, major)

    # عرض منفذ عرض (viewport) عشوائي
    sched_width = random.randint(1180, 1280)
    letter_width = random.randint(1250, 1350)

    schedule_png = _html_to_png(schedule_html, width=sched_width)
    letter_png = _html_to_png(letter_html, width=letter_width, height=1600)

    return [
        {"file_name": _random_filename("schedule"), "data": schedule_png},
        {"file_name": _random_filename("enrollment"), "data": letter_png},
    ]


if __name__ == '__main__':
    import sys
    import io

    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("يتم الآن اختبار توليد مستندات متعددة لـ PSU...")

    first_name = "John"
    last_name = "Smith"

    print(f"الاسم: {first_name} {last_name}")
    print(f"معرف PSU: {generate_psu_id()}")
    print(f"البريد الإلكتروني: {generate_psu_email(first_name, last_name)}")

    try:
        assets = generate_images(first_name, last_name)
        for asset in assets:
            with open(asset["file_name"], 'wb') as f:
                f.write(asset["data"])
            print(f"تم بنجاح! {asset['file_name']} ({len(asset['data'])} bytes)")
    except Exception as e:
        print(f"خطأ: {e}")
