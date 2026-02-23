"""مولد مستندات الطالب بصيغة PNG - نظام LionPATH لجامعة ولاية بنسلفانيا (مكافحة الاحتيال، مستندات متعددة)"""
import random
import string
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance


def _postprocess_image(png_bytes: bytes) -> bytes:
    """معالجة لقطة الشاشة لتبدو وكأنها صورة/مسح ضوئي حقيقي جدًا للتغلب على كشف التزوير الذكي.
    """
    img = Image.open(BytesIO(png_bytes)).convert('RGB')
    w, h = img.size

    # 1. دوران عشوائي أقوى قليلاً (يحاكي صورة ممسوحة ضوئياً بشكل سيء)
    angle = random.uniform(-2.5, 2.5)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
    
    # 2. هوامش قص عشوائية أقوى
    crop_left = random.randint(5, 25)
    crop_top = random.randint(5, 25)
    crop_right = random.randint(5, 25)
    crop_bottom = random.randint(5, 25)
    img = img.crop((crop_left, crop_top, img.width - crop_right, img.height - crop_bottom))

    # 3. محاكاة تباين وإضاءة الماسح الضوئي (Scanner Artifacts)
    brightness = random.uniform(0.9, 1.1)
    contrast = random.uniform(0.85, 1.15)
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)

    # 4. إضافة ضوضاء قوية وملونة (يحاكي كاميرا هاتف رديئة أو ضجيج Jpeg)
    arr = np.array(img, dtype=np.float32)
    noise_strength = random.uniform(3.0, 8.0)
    noise = np.random.normal(0, noise_strength, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # 5. ضبابية غاوسية متغيرة (محاكاة عدم ثبات اليد)
    blur_radius = random.uniform(0.5, 1.2)
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 6. إضافة "تظليل دقيق" لمحاكاة ورقة مطوية أو إضاءة غير متساوية (Vignette-like)
    import math
    if random.choice([True, False]):
        arr = np.array(img, dtype=np.float32)
        center_x, center_y = w / 2, h / 2
        for y in range(min(h, arr.shape[0])):
            for x in range(min(w, arr.shape[1])):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                # تغميق الزوايا قليلاً جداً
                fade = max(0.90, 1.0 - (dist / (max(w, h)) * 0.15))
                arr[y, x] = arr[y, x] * fade
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    # 7. تشوهات ضغط JPEG قوية (Compression Artifacts) مرتين
    jpeg_quality1 = random.randint(60, 75)
    jpeg_buf1 = BytesIO()
    img.save(jpeg_buf1, format='JPEG', quality=jpeg_quality1)
    jpeg_buf1.seek(0)
    img = Image.open(jpeg_buf1)
    
    jpeg_quality2 = random.randint(75, 85)
    jpeg_buf2 = BytesIO()
    img.save(jpeg_buf2, format='JPEG', quality=jpeg_quality2)
    jpeg_buf2.seek(0)
    img = Image.open(jpeg_buf2)

    # التصدير النهائي بصيغة PNG
    out_buf = BytesIO()
    img.save(out_buf, format='PNG')
    return out_buf.getvalue()


def generate_psu_id():
    """توليد معرف PSU عشوائي (9 أرقام)"""
    return f"9{random.randint(10000000, 99999999)}"


def generate_school_email(first_name, last_name, school_domain):
    """توليد بريد إلكتروني جامعي عشوائي بناءً على النطاق."""
    digit_count = random.choice([2, 3, 4])
    digits = ''.join([str(random.randint(0, 9)) for _ in range(digit_count)])
    
    # تنسيقات مختلفة للبريد
    formats = [
        f"{first_name.lower()}.{last_name.lower()}{digits}@{school_domain}",
        f"{first_name.lower()[0]}{last_name.lower()}{digits}@{school_domain}",
        f"{last_name.lower()}{first_name.lower()[0]}{digits}@{school_domain}",
        f"{first_name.lower()}{digits}@{school_domain}"
    ]
    return random.choice(formats)


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
    """توليد HTML لجدول دراسي مع توزيع مرئي عشوائي واسم الجامعة الصحيح."""
    
    # جلب تفاصيل الجامعة من الإعدادات أو استخدام قيم افتراضية
    from . import config
    school_info = config.SCHOOLS.get(school_id, config.SCHOOLS[config.DEFAULT_SCHOOL_ID])
    school_name = school_info['name']
    school_domain = school_info.get('domain', 'edu')
    
    # اسم مختصر للجامعة للشعار (مثلاً MIT أو أول كلمة)
    short_name = "".join([word[0] for word in school_name.split() if word[0].isupper()])
    if len(short_name) < 2:
        short_name = school_name.split()[0]
        
    # رابط شعار الجامعة الحقيقي (عبر خدمة Clearbit)
    logo_url = f"https://logo.clearbit.com/{school_domain}?size=100"
    
    student_id = generate_psu_id()
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
    
    # اسم نظام الطلاب العشوائي
    system_names = ["Student Center", "Portal", "MyCampus", "Connect", "Online Services", "Access"]
    system_name = random.choice(system_names)

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

    # عشوائية تنسيقات الخطوط والألوان في الجدول
    font_families = [
        '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
        '"Helvetica Neue", Helvetica, Arial, sans-serif',
        'Arial, Helvetica, sans-serif',
        '"Trebuchet MS", "Lucida Sans Unicode", "Lucida Grande", "Lucida Sans", Arial, sans-serif'
    ]
    font_family = random.choice(font_families)
    
    # تحريك العناصر عشوائياً بمقدار بيكسلات بسيطة
    margin_top_header = random.randint(15, 30)
    padding_content = random.randint(20, 45)
    psu_blue = random.choice(["#1E407C", "#1a3668", "#152c55", "#0f2347"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{school_name} - {system_name}</title>
    <style>
        :root {{
            --primary-color: {psu_blue};
            --bg-gray: {bg_gray};
            --text-color: #333;
        }}

        body {{
            font-family: {font_family};
            background-color: {bg_gray};
            margin: 0;
            padding: {random.randint(10,35)}px;
            color: var(--text-color);
            display: flex;
            justify-content: center;
        }}

        .viewport {{
            width: 100%;
            max-width: {random.randint(1050, 1150)}px;
            background-color: #fff;
            box-shadow: 0 {random.randint(2,8)}px {random.randint(10,30)}px rgba(0,0,0,{random.uniform(0.1, 0.2):.2f});
            min-height: 800px;
            display: flex;
            flex-direction: column;
        }}

        .header {{
            background-color: var(--primary-color);
            color: white;
            padding: 0 {random.randint(15, 25)}px;
            height: {random.randint(55,70)}px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: {random.randint(10, 20)}px;
        }}

        .school-logo-img {{
            height: {random.randint(28, 35)}px;
            width: auto;
            border-right: 1px solid rgba(255,255,255,0.3);
            padding-right: {random.randint(10, 20)}px;
            background-color: transparent;
            object-fit: contain;
        }}

        .system-name {{
            font-size: {random.randint(16,20)}px;
            font-weight: {random.choice(["300", "400", "normal"])};
        }}

        .user-menu {{
            font-size: {random.choice(["13px","14px","15px"])};
            display: flex;
            align-items: center;
            gap: {random.randint(15, 25)}px;
        }}

        .nav-bar {{
            background-color: {random.choice(["#f8f8f8", "#f4f4f4", "#fefefe", "#fafafa"])};
            border-bottom: 1px solid #ddd;
            padding: {random.randint(8,15)}px 20px;
            font-size: {body_font_size};
            color: #555;
            display: flex;
            gap: {random.randint(15, 30)}px;
        }}
        .nav-item {{ cursor: pointer; }}
        .nav-item.active {{ color: var(--primary-color); font-weight: bold; border-bottom: {random.choice(["2px","3px"])} solid var(--primary-color); padding-bottom: {random.randint(5,10)}px; }}

        .content {{
            padding: {padding_content}px;
            flex: 1;
        }}

        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: {margin_top_header}px;
            border-bottom: 1px solid #eee;
            padding-bottom: {random.randint(8,15)}px;
        }}

        .page-title {{
            font-size: {random.randint(20,28)}px;
            color: var(--primary-color);
            margin: 0;
            font-weight: {random.choice(["bold", "600", "500"])};
        }}

        .term-selector {{
            background: #fff;
            border: 1px solid #ccc;
            padding: {random.randint(4,8)}px {random.randint(8,15)}px;
            border-radius: {random.randint(0,4)}px;
            font-size: 14px;
            color: #333;
        }}

        .student-card {{
            background: {content_bg};
            border: 1px solid #e0e0e0;
            padding: {random.randint(12, 18)}px;
            margin-bottom: {random.randint(20, 30)}px;
            display: grid;
            grid-template-columns: repeat({random.choice([3, 4, 4])}, 1fr);
            gap: {random.randint(15, 25)}px;
            font-size: {body_font_size};
            border-radius: {random.randint(0,6)}px;
        }}
        .info-label {{ color: {random.choice(["#666","#777","#888"])}; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px;}}
        .info-val {{ font-weight: {random.choice(["bold", "600"])}; color: #222; font-size: {random.choice(["13px","14px","15px"])}; }}
        .status-badge {{
            background-color: {status_bg}; color: {status_color};
            padding: 3px {random.randint(6,10)}px; border-radius: {random.randint(3,10)}px; font-weight: bold; border: 1px solid {status_border};
            display: inline-block;
        }}

        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: {body_font_size};
            margin-top: {random.randint(10,25)}px;
        }}

        .schedule-table th {{
            text-align: left;
            padding: {random.randint(10,15)}px;
            background-color: {random.choice(["#f0f0f0", "#ececec", "#f5f5f5", "#eeeeee"])};
            border-bottom: 2px solid {random.choice(["#ccc", "#bbb", "#ddd"])};
            color: #444;
            font-weight: {random.choice(["bold", "600"])};
        }}

        .schedule-table td {{
            padding: {random.randint(12,18)}px 12px;
            border-bottom: 1px solid #eee;
            color: #333;
        }}

        .course-code {{ font-weight: bold; color: var(--primary-color); }}
        .course-title {{ font-weight: {random.choice(["500", "normal"])}; }}

        .total-row {{
            font-weight: bold;
            background-color: {random.choice(["#f8f8f8", "#fcfcfc", "#fdfdfd"])};
            color: #222;
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
            <img src="{logo_url}" alt="" class="school-logo-img" onerror="this.onerror=null; this.style.display='none'; document.getElementById('fb-logo1').style.display='block';">
            <div id="fb-logo1" style="display:none;font-family:'Georgia',serif;font-size:22px;font-weight:bold;line-height:30px;border-right:1px solid rgba(255,255,255,0.3);padding-right:15px;letter-spacing:1px;">{short_name}</div>
            <div class="system-name">{system_name}</div>
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
                <div class="info-label">Student ID</div>
                <div class="info-val">{student_id}</div>
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
            &copy; {current_year} {school_name}. All rights reserved.<br>
            {system_name} is the student information system for {short_name}.
        </div>
    </div>
</div>

</body>
</html>
"""
    return html


def generate_enrollment_letter_html(first_name, last_name, school_id='2565'):
    """توليد HTML لرسالة التحقق من التسجيل الرسمية للجامعة المختارة."""
    from . import config
    school_info = config.SCHOOLS.get(school_id, config.SCHOOLS[config.DEFAULT_SCHOOL_ID])
    school_name = school_info['name']
    school_domain = school_info.get('domain', 'edu')
    
    # استخراج شعار الجامعة الحقيقي
    logo_url = f"https://logo.clearbit.com/{school_domain}?size=150"
    
    # استخراج حرف من اسم الجامعة للشعار البديل
    school_initial = school_name[0]
    
    student_id = generate_psu_id()
    name = f"{first_name} {last_name}"
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    semester, _ = _get_current_semester()
    standing = random.choice(ACADEMIC_STANDINGS)

    # تفاصيل تسجيل عشوائية
    major = random.choice(MAJORS)
    credits_earned = random.randint(24, 95)
    credits_attempted = credits_earned + random.randint(0, 6)
    gpa = round(random.uniform(2.8, 3.95), 2)
    expected_grad_year = now.year + random.randint(1, 3)
    expected_grad_month = random.choice(["May", "December"])
    enroll_year = now.year - random.randint(1, 4)
    enroll_month = random.choice(["August", "January"])
    report_id = f"LPR-{random.randint(10000, 99999)}-{random.randint(100, 999)}"

    # عشوائية في الحروف وتنسيق المستند الثاني لإبطال بصمة القوالب
    font_family_letter = random.choice([
        '"Times New Roman", Times, serif',
        '"Helvetica Neue", Helvetica, Arial, sans-serif',
        'Cambria, Cochin, Georgia, Times, "Times New Roman", serif',
        'Arial, Helvetica, sans-serif'
    ])
    
    psu_logo_color = random.choice(["#1E407C", "#152c55", "#0f2347", "#17366b"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{short_name if 'short_name' in locals() else school_name} - Official Enrollment Verification</title>
    <style>
        body {{
            font-family: {font_family_letter};
            background-color: {random.choice(["#f4f4f4", "#f0f0f0", "#e8e8e8", "#f9f9f9"])};
            margin: 0;
            padding: {random.randint(15, 30)}px;
            display: flex;
            justify-content: center;
        }}

        .page {{
            width: 8.5in;
            min-height: 11in;
            background: white;
            padding: {random.uniform(0.8, 1.2):.2f}in;
            box-sizing: border-box;
            box-shadow: 0 {random.randint(3,6)}px {random.randint(10,20)}px rgba(0,0,0,{random.uniform(0.1, 0.2):.2f});
            color: {random.choice(["#222", "#333", "#111"])};
            position: relative;
        }}

        .header {{
            margin-bottom: {random.randint(30, 50)}px;
            border-bottom: {random.choice(["1px", "2px"])} solid {random.choice(["#ccc", "#bbb", "var(--psu-blue)"])};
            padding-bottom: {random.randint(15, 25)}px;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            margin-bottom: {random.randint(10, 20)}px;
        }}

        .school-logo-img {{
            width: {random.randint(55, 65)}px;
            height: auto;
            max-height: {random.randint(55, 65)}px;
            margin-right: {random.randint(15, 25)}px;
            object-fit: contain;
        }}

        .org-name {{
            font-size: {random.randint(17, 20)}px;
            font-weight: bold;
            color: {psu_logo_color};
            text-transform: uppercase;
            letter-spacing: {random.uniform(0, 1):.1f}px;
        }}

        .reg-address {{
            font-size: {random.choice(["10.5pt", "11pt", "10pt"])};
            color: #555;
            line-height: {random.uniform(1.3, 1.6):.1f};
            text-align: right;
            position: absolute;
            top: {random.uniform(0.9, 1.1):.2f}in;
            right: {random.uniform(0.9, 1.1):.2f}in;
        }}

        .content {{
            font-size: {random.choice(["11pt", "11.5pt", "12pt"])};
            line-height: {random.uniform(1.5, 1.8):.2f};
        }}

        .title {{
            font-size: {random.randint(16, 20)}px;
            font-weight: bold;
            text-align: center;
            margin: {random.randint(25, 40)}px 0;
            text-transform: uppercase;
            text-decoration: underline;
            letter-spacing: {random.uniform(0, 1.5):.1f}px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: {random.randint(25, 35)}px 0;
            font-size: {random.choice(["11pt", "11.5pt"])};
        }}

        .data-table td {{
            padding: {random.randint(7, 10)}px 5px;
            border-bottom: 1px solid {random.choice(["#eee", "#ddd", "#f5f5f5"])};
        }}

        .data-label {{
            font-weight: {random.choice(["bold", "600"])};
            width: {random.choice(["40%", "45%", "35%"])};
            color: #444;
        }}

        .data-value {{
            font-weight: {random.choice(["600", "500", "normal"])};
            color: #111;
        }}

        .footer {{
            position: absolute;
            bottom: {random.uniform(0.7, 1.0):.2f}in;
            left: 1in;
            right: 1in;
            font-size: {random.choice(["8pt", "9pt", "10pt"])};
            color: {random.choice(["#777", "#888", "#999"])};
            text-align: center;
            border-top: 1px solid #ddd;
            padding-top: {random.randint(8, 15)}px;
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
            <img src="{logo_url}" alt="" class="school-logo-img" onerror="this.onerror=null; this.style.display='none'; document.getElementById('fb-logo2').style.display='flex';">
            <div id="fb-logo2" style="display:none; width:50px; height:50px; background-color:{psu_logo_color}; border-radius:50%; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:28px; font-family:serif; margin-right:20px;">{school_initial}</div>
            <div class="org-name">{school_name}</div>
        </div>
        <div class="reg-address">
            <strong>Office of the University Registrar</strong><br>
            Student Services Building<br>
            {school_info.get('city', 'University City')}, {school_info.get('state', 'State')}<br>
            Phone: (814) {random.randint(100, 999)}-{random.randint(1000, 9999)}
        </div>
    </div>

    <div class="content">
        <div style="margin-bottom: 20px;">{date_str}</div>

        <div style="margin-bottom: 20px;">
            <strong>To Whom It May Concern:</strong>
        </div>

        <p>
            This letter is to verify the enrollment status of the student listed below
            at {school_name}. This information is generated from the
            University's official student information records.
        </p>

        <div class="title">Enrollment Verification</div>

        <table class="data-table">
            <tr>
                <td class="data-label">Student Name:</td>
                <td class="data-value">{name}</td>
            </tr>
            <tr>
                <td class="data-label">Student ID:</td>
                <td class="data-value">{student_id}</td>
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
            The student listed above is currently enrolled and in {standing.lower()} at {school_name}.
            Should you require further information, authorized requests may be submitted
            to the Office of the University Registrar.
        </p>

        <div style="margin-top: 50px;">
            Sincerely,
        </div>
        <div style="margin-top: 10px;">
            <strong>Office of the University Registrar</strong><br>
            {school_name}
        </div>
    </div>

    <div class="footer">
        Generated by official student records for {school_name} | Report ID: {report_id} | {date_str}<br>
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
            page.wait_for_load_state('networkidle', timeout=15000)

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
    """توليد مستندين: لقطة شاشة للجدول + رسالة التسجيل للجامعة المطلوبة."""
    
    schedule_html = generate_schedule_html(first_name, last_name, school_id)
    letter_html = generate_enrollment_letter_html(first_name, last_name, school_id)

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
