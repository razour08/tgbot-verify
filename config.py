"""ملف التكوين العام (Global Configuration)"""
import os
from dotenv import load_dotenv

# تحميل ملف .env
load_dotenv()

# تكوين روبوت تيليجرام (Telegram Bot)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "your_channel_username")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")

# تكوين المسؤول (Admin)
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))

# تكوين النقاط (Points/Balance)
VERIFY_COST = 1  # النقاط المستهلكة في التحقق
CHECKIN_REWARD = 1  # مكافأة نقاط تسجيل الدخول اليومي (Check-in)
INVITE_REWARD = 2  # مكافأة نقاط الدعوة
REGISTER_REWARD = 1  # مكافأة نقاط التسجيل

# رابط المساعدة
HELP_NOTION_URL = "https://rhetorical-era-3f3.notion.site/dd78531dbac745af9bbac156b51da9cc"
