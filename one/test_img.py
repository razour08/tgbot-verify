import sys
import os

# إضافة المجلد الرئيسي للمسارات
sys.path.insert(0, os.getcwd())

try:
    from one.name_generator import NameGenerator
    from one.img_generator import generate_images, generate_psu_id, generate_school_email
    from one import config
    
    # 1. توليد اسم عشوائي
    name_data = NameGenerator.generate()
    first_name = name_data["first_name"]
    last_name = name_data["last_name"]
    
    # 2. الحصول على مدرسة عشوائية
    school_id = config.get_random_school_id()
    school_name = config.SCHOOLS[school_id]["name"]
    
    psu_id = generate_psu_id()
    email = generate_school_email(first_name, last_name, config.SCHOOLS[school_id]["domain"])
    
    print("=" * 50)
    print("معلومات الطالب المولدة (كما في الإنتاج):")
    print(f"الاسم: {first_name} {last_name}")
    print(f"المدرسة: {school_name} (ID: {school_id})")
    print(f"البريد الإلكتروني: {email}")
    print(f"رقم الطالب الجامعي (PSU ID): {psu_id}")
    print("=" * 50)
    
    print("\nجاري توليد المستندات باحترافية (للتغلب على كشف التزوير)...")
    
    # 3. تمرير المتغيرات العشوائية إلى دالة توليد الصور
    assets = generate_images(first_name, last_name, school_id)
    
    # 4. حفظ الصور
    save_dir = r'C:\Users\ramzi.dekali\.gemini\antigravity\brain\5a99cc60-027f-429f-90d7-678d6048f88a'
    for asset in assets:
        path = os.path.join(save_dir, 'simulated_' + asset['file_name'])
        with open(path, 'wb') as f:
            f.write(asset['data'])
        print(f"✅ تم حفظ الصورة المحسنة في:")
        print(f"   {path}")
        
except Exception as e:
    print(f"❌ حدث خطأ: {e}")