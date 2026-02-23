# بوت تيليجرام للتحقق التلقائي من SheerID

![Stars](https://img.shields.io/github/stars/PastKing/tgbot-verify?style=social)
![Forks](https://img.shields.io/github/forks/PastKing/tgbot-verify?style=social)
![Issues](https://img.shields.io/github/issues/PastKing/tgbot-verify)
![License](https://img.shields.io/github/license/PastKing/tgbot-verify)

> 🤖 بوت تيليجرام للتحقق التلقائي من هوية الطلاب/المعلمين عبر منصة SheerID
> 
> مبني على إصدار سابق مع العديد من التحسينات والميزات الجديدة.

[中文文档](README_ZH.md) | [English](README_EN.md) | العربية

---

## 📋 نظرة عامة

هذا بوت تيليجرام مبني بلغة Python، يقوم بالتحقق التلقائي من هوية الطلاب/المعلمين عبر منصة SheerID لعدة منصات خدمية. يقوم البوت بإنشاء معلومات الهوية تلقائياً، وإنشاء مستندات التحقق، وتقديمها إلى منصة SheerID، مما يُبسّط عملية التحقق بشكل كبير.

> **⚠️ ملاحظة مهمة**:
> 
> - خدمات مثل **Gemini One Pro** و **ChatGPT Teacher K12** و **Spotify Student** و **YouTube Premium Student** تتطلب تحديث بيانات التحقق (مثل `programId`) في ملف إعدادات كل وحدة قبل الاستخدام. يرجى مراجعة قسم "يجب قراءته قبل الاستخدام" أدناه.
> - يوفر هذا المشروع أيضاً نهج التنفيذ ووثائق API الخاصة بـ **تحقق ChatGPT العسكري**. للمزيد من التفاصيل، يرجى مراجعة [`military/README.md`](military/README.md). يمكن للمستخدمين الدمج بناءً على الوثائق.

### 🎯 الخدمات المدعومة

| الأمر | الخدمة | النوع | الحالة | الوصف |
|-------|--------|-------|--------|-------|
| `/verify` | Gemini One Pro | معلم | ✅ مكتمل | خصم Google AI Studio التعليمي |
| `/verify2` | ChatGPT Teacher K12 | معلم | ✅ مكتمل | خصم OpenAI ChatGPT التعليمي |
| `/verify3` | Spotify Student | طالب | ✅ مكتمل | خصم اشتراك Spotify للطلاب |
| `/verify4` | Bolt.new Teacher | معلم | ✅ مكتمل | خصم Bolt.new التعليمي (استرجاع الكود تلقائياً) |
| `/verify5` | YouTube Premium Student | طالب | ⚠️ تجريبي | خصم YouTube Premium للطلاب (انظر الملاحظات أدناه) |

> **⚠️ ملاحظات خاصة بتحقق YouTube**:
> 
> تحقق YouTube حالياً في مرحلة تجريبية. يرجى قراءة [`youtube/HELP.MD`](youtube/HELP.MD) بعناية قبل الاستخدام.
> 
> **الاختلافات الرئيسية**:
> - صيغة رابط YouTube الأصلي تختلف عن الخدمات الأخرى
> - يتطلب استخراج `programId` و `verificationId` يدوياً من سجلات شبكة المتصفح
> - يجب إنشاء صيغة رابط SheerID القياسية يدوياً
> 
> **خطوات الاستخدام**:
> 1. قم بزيارة صفحة تحقق طلاب YouTube Premium
> 2. افتح أدوات المطور في المتصفح (F12) ← علامة تبويب الشبكة (Network)
> 3. ابدأ عملية التحقق، وابحث عن `https://services.sheerid.com/rest/v2/verification/`
> 4. استخرج `programId` من حمولة الطلب و `verificationId` من الاستجابة
> 5. أنشئ الرابط يدوياً: `https://services.sheerid.com/verify/{programId}/?verificationId={verificationId}`
> 6. أرسل الرابط باستخدام الأمر `/verify5`

> **💡 نهج تحقق ChatGPT العسكري**:
> 
> يوفر هذا المشروع نهج التنفيذ ووثائق API الخاصة بتحقق ChatGPT العسكري عبر SheerID. تختلف عملية التحقق العسكري عن تحقق الطلاب/المعلمين العادي، حيث تتطلب استدعاء API `collectMilitaryStatus` أولاً لتعيين الحالة العسكرية قبل تقديم المعلومات الشخصية. للاطلاع على نهج التنفيذ التفصيلي ووثائق API، يرجى مراجعة [`military/README.md`](military/README.md). يمكن للمستخدمين دمج هذا في البوت بناءً على الوثائق.

### ✨ الميزات الرئيسية

- 🚀 **عملية مؤتمتة**: إكمال بنقرة واحدة لإنشاء المعلومات والمستندات والتقديم
- 🎨 **إنشاء ذكي**: إنشاء تلقائي لصور بطاقات الطلاب/المعلمين بصيغة PNG
- 💰 **نظام نقاط**: طرق متعددة لكسب النقاط تشمل تسجيل الدخول اليومي والدعوات وأكواد الاسترداد
- 🔐 **آمن وموثوق**: قاعدة بيانات MySQL مع إعدادات متغيرات البيئة
- ⚡ **التحكم في التزامن**: إدارة ذكية للطلبات المتزامنة لضمان الاستقرار
- 👥 **ميزات الإدارة**: نظام كامل لإدارة المستخدمين والنقاط

---

## 🛠️ المكدس التقني

- **اللغة**: Python 3.11+
- **إطار البوت**: python-telegram-bot 20.0+
- **قاعدة البيانات**: MySQL 5.7+
- **أتمتة المتصفح**: Playwright
- **عميل HTTP**: httpx
- **معالجة الصور**: Pillow, reportlab, xhtml2pdf
- **إدارة البيئة**: python-dotenv

---

## 🚀 البدء السريع

### 1. استنساخ المشروع

```bash
git clone https://github.com/yourusername/your-repo.git
cd tgbot-verify
```

### 2. تثبيت المتطلبات

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. إعداد متغيرات البيئة

انسخ `env.example` إلى `.env` واملأ الإعدادات:

```env
# إعدادات بوت تيليجرام
BOT_TOKEN=your_bot_token_here
CHANNEL_USERNAME=your_channel
CHANNEL_URL=https://t.me/your_channel
ADMIN_USER_ID=your_admin_id

# إعدادات قاعدة بيانات MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=tgbot_verify
```

### 4. تشغيل البوت

```bash
python bot.py
```

---

## 🐳 النشر باستخدام Docker

يتضمن ملف `docker-compose.yml` خدمتين — لا حاجة لتثبيت MySQL خارجياً:

| الخدمة | الوصف | الصورة |
|--------|-------|--------|
| `mysql` | قاعدة بيانات MySQL 8.0 (مع فحص صحي وتخزين دائم) | mysql:8.0 |
| `tgbot` | بوت تيليجرام للتحقق | بناء محلي |

### المتطلبات الأساسية

- تثبيت [Docker](https://docs.docker.com/get-docker/) و Docker Compose plugin
- الحصول على رمز بوت تيليجرام (عبر [@BotFather](https://t.me/BotFather))
- الحصول على معرف تيليجرام الخاص بك (عبر [@userinfobot](https://t.me/userinfobot))

### باستخدام Docker Compose (مُوصى به)

```bash
# 1. استنساخ المشروع
git clone https://github.com/yourusername/your-repo.git
cd tgbot-verify

# 2. إعداد متغيرات البيئة
cp env.example .env
nano .env    # املأ BOT_TOKEN و ADMIN_USER_ID و MYSQL_PASSWORD وغيرها

# 3. بناء وتشغيل جميع الخدمات (MySQL + البوت)
docker compose up -d --build

# 4. عرض السجلات
docker compose logs -f

# 5. التحقق من حالة الخدمات
docker compose ps
```

> **⚠️ ملاحظة**: إصدارات Docker الحديثة تستخدم `docker compose` (بمسافة). إذا لم يُعثر على `docker-compose`، ثبّت الإضافة:
> ```bash
> sudo apt install docker-compose-plugin
> ```

### الأوامر المفيدة

| الأمر | الوصف |
|-------|-------|
| `docker compose up -d --build` | بناء وتشغيل جميع الخدمات |
| `docker compose logs -f` | عرض السجلات في الوقت الحقيقي |
| `docker compose logs -f tgbot` | عرض سجلات البوت فقط |
| `docker compose ps` | التحقق من حالة الخدمات |
| `docker compose restart tgbot` | إعادة تشغيل البوت فقط |
| `docker compose down` | إيقاف جميع الخدمات |
| `docker compose down -v` | إيقاف وحذف البيانات (⚠️ يحذف قاعدة البيانات) |

### النشر اليدوي باستخدام Docker

إذا لم تستخدم Docker Compose، تحتاج لتوفير قاعدة بيانات MySQL بنفسك:

```bash
# بناء الصورة
docker build -t tgbot-verify .

# تشغيل الحاوية (يتطلب MySQL خارجي)
docker run -d \
  --name tgbot-verify \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  tgbot-verify
```

---

## 📖 دليل الاستخدام

### أوامر المستخدم

```bash
/start              # بدء الاستخدام (التسجيل)
/about              # معرفة المزيد عن ميزات البوت
/balance            # التحقق من رصيد النقاط
/qd                 # تسجيل الدخول اليومي (+1 نقطة)
/invite             # إنشاء رابط دعوة (+2 نقطة لكل شخص)
/use <كود>          # استرداد النقاط بالكود
/status             # عرض سجل طلبات التحقق
/verify <رابط>      # تحقق Gemini One Pro
/verify2 <رابط>     # تحقق ChatGPT Teacher K12
/verify3 <رابط>     # تحقق Spotify Student
/verify4 <رابط>     # تحقق Bolt.new Teacher
/verify5 <رابط>     # تحقق YouTube Premium Student
/check <id>         # استعلام نتيجة أي تحقق
/getV4Code <id>     # كود Bolt.new (اسم بديل لـ /check)
/help               # عرض معلومات المساعدة
```

### أوامر المسؤول

```bash
/addbalance <معرف_المستخدم> <نقاط>             # إضافة نقاط للمستخدم
/block <معرف_المستخدم>                          # حظر مستخدم
/white <معرف_المستخدم>                          # إلغاء حظر مستخدم
/blacklist                                      # عرض القائمة السوداء
/genkey <كود> <نقاط> [عدد_مرات] [أيام]          # إنشاء كود استرداد
/listkeys                                       # عرض قائمة أكواد الاسترداد
/broadcast <نص>                                 # إرسال إشعار جماعي
```

### عملية التحقق

1. **الحصول على رابط التحقق**
   - قم بزيارة صفحة التحقق الخاصة بالخدمة المطلوبة
   - ابدأ عملية التحقق
   - انسخ عنوان URL الكامل من شريط عنوان المتصفح (يتضمن `verificationId`)

2. **تقديم طلب التحقق**
   ```
   /verify3 https://services.sheerid.com/verify/xxx/?verificationId=yyy
   ```

3. **انتظار المعالجة**
   - يقوم البوت بإنشاء معلومات الهوية تلقائياً
   - إنشاء صورة بطاقة الطالب/المعلم
   - التقديم إلى منصة SheerID

4. **الحصول على النتائج**
   - البوت ينتظر نتيجة المراجعة تلقائياً (حتى 60 ثانية)
   - في حالة النجاح يتم إرجاع رابط إعادة التوجيه أو كود التفعيل
   - إذا انتهت المهلة، استخدم `/check <id>` للاستعلام لاحقاً

---

## 📁 هيكل المشروع

```
tgbot-verify/
├── bot.py                  # البرنامج الرئيسي للبوت
├── config.py               # الإعدادات العامة
├── database_mysql.py       # إدارة قاعدة بيانات MySQL
├── .env                    # متغيرات البيئة (يجب إنشاؤه يدوياً)
├── env.example             # قالب متغيرات البيئة
├── requirements.txt        # متطلبات Python
├── Dockerfile              # بناء صورة Docker
├── docker-compose.yml      # إعدادات Docker Compose
├── handlers/               # معالجات الأوامر
│   ├── user_commands.py    # أوامر المستخدم
│   ├── admin_commands.py   # أوامر المسؤول
│   └── verify_commands.py  # أوامر التحقق
├── one/                    # وحدة تحقق Gemini One Pro
├── k12/                    # وحدة تحقق ChatGPT K12
├── spotify/                # وحدة تحقق Spotify Student
├── youtube/                # وحدة تحقق YouTube Premium
├── Boltnew/                # وحدة تحقق Bolt.new
├── military/               # وثائق نهج تحقق ChatGPT العسكري
└── utils/                  # الدوال المساعدة
    ├── messages.py         # قوالب الرسائل
    ├── concurrency.py      # التحكم في التزامن
    └── checks.py           # التحقق من الصلاحيات
```

---

## ⚙️ الإعدادات

### متغيرات البيئة

| المتغير | مطلوب | الوصف | القيمة الافتراضية |
|---------|-------|-------|-------------------|
| `BOT_TOKEN` | ✅ | رمز بوت تيليجرام | - |
| `CHANNEL_USERNAME` | ❌ | اسم مستخدم القناة | your_channel_username |
| `CHANNEL_URL` | ❌ | رابط القناة | https://t.me/your_channel |
| `ADMIN_USER_ID` | ✅ | معرف تيليجرام للمسؤول | - |
| `MYSQL_HOST` | ✅ | عنوان خادم MySQL | localhost |
| `MYSQL_PORT` | ❌ | منفذ MySQL | 3306 |
| `MYSQL_USER` | ✅ | اسم مستخدم MySQL | - |
| `MYSQL_PASSWORD` | ✅ | كلمة مرور MySQL | - |
| `MYSQL_DATABASE` | ✅ | اسم قاعدة البيانات | tgbot_verify |

### إعدادات النقاط

يمكنك تخصيص قواعد النقاط في `config.py`:

```python
VERIFY_COST = 1        # النقاط المستهلكة للتحقق
CHECKIN_REWARD = 1     # نقاط مكافأة تسجيل الدخول اليومي
INVITE_REWARD = 2      # نقاط مكافأة الدعوة
REGISTER_REWARD = 1    # نقاط مكافأة التسجيل
```

---

## ⚠️ ملاحظات مهمة

### 🔴 يجب قراءته قبل الاستخدام

**قبل استخدام البوت، يرجى التحقق من إعدادات التحقق وتحديثها في كل وحدة!**

نظراً لأن `programId` الخاص بمنصة SheerID قد يتم تحديثه دورياً، **يجب** تحديث بيانات التحقق في ملفات الإعدادات للخدمات التالية قبل الاستخدام:

- `one/config.py` - تحقق **Gemini One Pro** (تحديث `PROGRAM_ID`)
- `k12/config.py` - تحقق **ChatGPT Teacher K12** (تحديث `PROGRAM_ID`)
- `spotify/config.py` - تحقق **Spotify Student** (تحديث `PROGRAM_ID`)
- `youtube/config.py` - تحقق **YouTube Premium Student** (تحديث `PROGRAM_ID`)
- `Boltnew/config.py` - تحقق Bolt.new Teacher (يُنصح بالتحقق من `PROGRAM_ID`)

**كيفية الحصول على أحدث programId**:
1. قم بزيارة صفحة التحقق الخاصة بالخدمة المطلوبة
2. افتح أدوات المطور في المتصفح (F12) ← علامة تبويب الشبكة (Network)
3. ابدأ عملية التحقق
4. ابحث عن طلبات `https://services.sheerid.com/rest/v2/verification/`
5. استخرج `programId` من عنوان URL أو حمولة الطلب
6. حدّث ملف `config.py` الخاص بالوحدة المعنية

> **تلميح**: إذا استمر فشل التحقق، فمن المرجح أن `programId` قد انتهت صلاحيته. يرجى تحديثه باتباع الخطوات أعلاه.

---

## 🔗 روابط

- 📺 **قناة تيليجرام**: https://t.me/your_channel
- 🐛 **تتبع المشاكل**: [GitHub Issues](https://github.com/yourusername/your-repo/issues)
- 📖 **دليل النشر**: [DEPLOY.md](DEPLOY.md)

---

## 🤝 التطوير الثانوي

مرحباً بالتطوير الثانوي! يرجى اتباع القواعد التالية:

1. **الحفاظ على معلومات المؤلف الأصلي**
   - الاحتفاظ بعنوان المستودع الأصلي في الكود والوثائق
   - الإشارة إلى أنه مبني على هذا المشروع

2. **رخصة المصدر المفتوح**
   - يستخدم هذا المشروع رخصة MIT
   - مشاريع التطوير الثانوي يجب أن تكون مفتوحة المصدر أيضاً

3. **الاستخدام التجاري**
   - مجاني للاستخدام الشخصي
   - الاستخدام التجاري يتطلب التحسين الذاتي وتحمل المسؤولية
   - لا يتم تقديم أي دعم فني أو ضمانات

---

## 📜 الرخصة

هذا المشروع مرخص بموجب [رخصة MIT](LICENSE).

```
MIT License

Copyright (c) 2025 PastKing

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 شكر وتقدير

- شكراً لجميع المساهمين في تطوير هذا المشروع.
- شكراً لجميع المطورين الذين ساهموا في هذا المشروع
- شكراً لمنصة SheerID على تقديم خدمات التحقق

---

## 📊 إحصائيات

[![Star History Chart](https://api.star-history.com/svg?repos=PastKing/tgbot-verify&type=Date)](https://star-history.com/#PastKing/tgbot-verify&Date)

---

## 📝 سجل التحديثات

### v2.1.0 (2025-02-18)

- ✨ إضافة أمر `/check`: استعلام نتيجة أي تحقق بالمعرف
- ✨ إضافة أمر `/status`: عرض سجل طلبات التحقق
- 🚀 الانتظار التلقائي: البوت ينتظر نتيجة التحقق تلقائياً (حتى 60 ثانية)
- 🎯 تحسين معدل نجاح Gemini One Pro: أسماء أمريكية حقيقية، تدوير عشوائي للجامعات، فصل دراسي ديناميكي، مواد عشوائية
- 💬 جميع رسائل البوت أصبحت ثنائية اللغة (EN/AR)
- 📝 تحسين رسائل الأخطاء مع تفاصيل SheerID أوضح

### v2.0.0 (2025-01-12)

- ✨ إضافة تحقق Spotify Student و YouTube Premium Student (YouTube في مرحلة تجريبية، راجع youtube/HELP.MD)
- 🚀 تحسين التحكم في التزامن والأداء
- 📝 تحسين الوثائق ودليل النشر
- 🐛 إصلاح أخطاء معروفة

### v1.0.0

- 🎉 الإصدار الأولي
- ✅ دعم تحقق Gemini و ChatGPT و Bolt.new

---

<p align="center">
  <strong>⭐ إذا كان هذا المشروع مفيداً لك، يرجى منحه نجمة (Star)!</strong>
</p>

<p align="center">
  صنع بـ ❤️
</p>
