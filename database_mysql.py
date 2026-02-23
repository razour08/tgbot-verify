"""تنفيذ قاعدة بيانات MySQL

استخدام خادم MySQL المُوفّر لتخزين البيانات
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

logger = logging.getLogger(__name__)


class MySQLDatabase:
    """فئة إدارة قاعدة بيانات MySQL"""

    def __init__(self):
        """تهيئة اتصال قاعدة البيانات"""
        import os
        
        # قراءة التكوين من متغيرات البيئة (مستحسن) أو استخدام القيم الافتراضية
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'tgbot_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'your_password_here'),
            'database': os.getenv('MYSQL_DATABASE', 'tgbot_verify'),
            'charset': 'utf8mb4',
            'autocommit': False,
        }
        logger.info(f"تمت تهيئة قاعدة بيانات MySQL: {self.config['user']}@{self.config['host']}/{self.config['database']}")
        self.init_database()

    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        return pymysql.connect(**self.config)

    def init_database(self):
        """تهيئة هيكل جداول قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # جدول المستخدمين (Users)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    full_name VARCHAR(255),
                    balance INT DEFAULT 1,
                    is_blocked TINYINT(1) DEFAULT 0,
                    invited_by BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_checkin DATETIME NULL,
                    INDEX idx_username (username),
                    INDEX idx_invited_by (invited_by)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # جدول سجلات الدعوات (Invitations)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invitations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    inviter_id BIGINT NOT NULL,
                    invitee_id BIGINT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_inviter (inviter_id),
                    INDEX idx_invitee (invitee_id),
                    FOREIGN KEY (inviter_id) REFERENCES users(user_id),
                    FOREIGN KEY (invitee_id) REFERENCES users(user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # جدول سجلات التحقق (Verifications)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS verifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    verification_type VARCHAR(50) NOT NULL,
                    verification_url TEXT,
                    verification_id VARCHAR(255),
                    status VARCHAR(50) NOT NULL,
                    result TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_type (verification_type),
                    INDEX idx_created (created_at),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # جدول مفاتيح البطاقات (Card Keys)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS card_keys (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    key_code VARCHAR(100) UNIQUE NOT NULL,
                    balance INT NOT NULL,
                    max_uses INT DEFAULT 1,
                    current_uses INT DEFAULT 0,
                    expire_at DATETIME NULL,
                    created_by BIGINT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_key_code (key_code),
                    INDEX idx_created_by (created_by)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            # سجل استخدام مفاتيح البطاقات
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS card_key_usage (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    key_code VARCHAR(100) NOT NULL,
                    user_id BIGINT NOT NULL,
                    used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_key_code (key_code),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

            conn.commit()
            logger.info("تم الانتهاء من تهيئة جداول قاعدة بيانات MySQL")

        except Exception as e:
            logger.error(f"فشل في تهيئة قاعدة البيانات: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def create_user(
        self, user_id: int, username: str, full_name: str, invited_by: Optional[int] = None
    ) -> bool:
        """إنشاء مستخدم جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (user_id, username, full_name, invited_by, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, username, full_name, invited_by),
            )

            if invited_by:
                cursor.execute(
                    "UPDATE users SET balance = balance + 2 WHERE user_id = %s",
                    (invited_by,),
                )

                cursor.execute(
                    """
                    INSERT INTO invitations (inviter_id, invitee_id, created_at)
                    VALUES (%s, %s, NOW())
                    """,
                    (invited_by, user_id),
                )

            conn.commit()
            return True

        except pymysql.err.IntegrityError:
            conn.rollback()
            return False
        except Exception as e:
            logger.error(f"فشل في إنشاء المستخدم: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على معلومات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            
            if row:
                # إنشاء قاموس (dict) جديد وتحويل datetime إلى سلسلة نصية بتنسيق ISO
                result = dict(row)
                if result.get('created_at'):
                    result['created_at'] = result['created_at'].isoformat()
                if result.get('last_checkin'):
                    result['last_checkin'] = result['last_checkin'].isoformat()
                return result
            return None

        finally:
            cursor.close()
            conn.close()

    def user_exists(self, user_id: int) -> bool:
        """التحقق مما إذا كان المستخدم موجوداً"""
        return self.get_user(user_id) is not None

    def is_user_blocked(self, user_id: int) -> bool:
        """التحقق مما إذا كان المستخدم محظوراً"""
        user = self.get_user(user_id)
        return user and user["is_blocked"] == 1

    def block_user(self, user_id: int) -> bool:
        """حظر المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = %s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"فشل في حظر المستخدم: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def unblock_user(self, user_id: int) -> bool:
        """إلغاء حظر المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = %s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"فشل في إلغاء الحظر: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_blacklist(self) -> List[Dict]:
        """الحصول على قائمة الحظر (Blacklist)"""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute("SELECT * FROM users WHERE is_blocked = 1")
            return list(cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    def add_balance(self, user_id: int, amount: int) -> bool:
        """زيادة رصيد/نقاط المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                (amount, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"فشل في إضافة النقاط: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def deduct_balance(self, user_id: int, amount: int) -> bool:
        """خصم نقاط المستخدم"""
        user = self.get_user(user_id)
        if not user or user["balance"] < amount:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE user_id = %s",
                (amount, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"فشل في خصم النقاط: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def can_checkin(self, user_id: int) -> bool:
        """التحقق مما إذا كان بإمكان المستخدم تسجيل الدخول اليوم"""
        user = self.get_user(user_id)
        if not user:
            return False

        last_checkin = user.get("last_checkin")
        if not last_checkin:
            return True

        last_date = datetime.fromisoformat(last_checkin).date()
        today = datetime.now().date()

        return last_date < today

    def checkin(self, user_id: int) -> bool:
        """تسجيل دخول المستخدم (إصلاح خلل تسجيل الدخول المتكرر (bug))"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # استخدام عملية ذرية (atomic SQL) لتجنب ظروف السباق (race conditions)
            # التحديث فقط عندما يكون last_checkin بقيمة NULL أو عندما يكون التاريخ < اليوم
            cursor.execute(
                """
                UPDATE users
                SET balance = balance + 1, last_checkin = NOW()
                WHERE user_id = %s 
                AND (
                    last_checkin IS NULL 
                    OR DATE(last_checkin) < CURDATE()
                )
                """,
                (user_id,),
            )
            conn.commit()
            
            # التحقق مما إذا تم التحديث فعلياً (affected_rows > 0 يعني نجاح العملية)
            success = cursor.rowcount > 0
            return success
            
        except Exception as e:
            logger.error(f"فشل تسجيل الدخول (Check-in): {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def add_verification(
        self, user_id: int, verification_type: str, verification_url: str,
        status: str, result: str = "", verification_id: str = ""
    ) -> bool:
        """إضافة سجل تحقق جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO verifications
                (user_id, verification_type, verification_url, verification_id, status, result, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (user_id, verification_type, verification_url, verification_id, status, result),
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"فشل في إضافة سجل التحقق: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_verifications(self, user_id: int) -> List[Dict]:
        """الحصول على سجلات الخاصه بالمستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute(
                """
                SELECT * FROM verifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    def create_card_key(
        self, key_code: str, balance: int, created_by: int,
        max_uses: int = 1, expire_days: Optional[int] = None
    ) -> bool:
        """إنشاء مفتاح بطاقة (Card Key/Promo Code)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            expire_at = None
            if expire_days:
                expire_at = datetime.now() + timedelta(days=expire_days)

            cursor.execute(
                """
                INSERT INTO card_keys (key_code, balance, max_uses, created_by, created_at, expire_at)
                VALUES (%s, %s, %s, %s, NOW(), %s)
                """,
                (key_code, balance, max_uses, created_by, expire_at),
            )
            conn.commit()
            return True

        except pymysql.err.IntegrityError:
            logger.error(f"مفتاح البطاقة موجود مسبقاً: {key_code}")
            conn.rollback()
            return False
        except Exception as e:
            logger.error(f"فشل في إنشاء مفتاح البطاقة: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def use_card_key(self, key_code: str, user_id: int) -> Optional[int]:
        """استخدام مفتاح البطاقة، وإرجاع عدد النقاط المكتسبة"""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            # الاستعلام عن مفتاح البطاقة
            cursor.execute(
                "SELECT * FROM card_keys WHERE key_code = %s",
                (key_code,),
            )
            card = cursor.fetchone()

            if not card:
                return None

            # التحقق مما إذا كان قديماً (منتهي الصلاحية)
            if card["expire_at"] and datetime.now() > card["expire_at"]:
                return -2

            # التحقق من عدد مرات الاستخدام
            if card["current_uses"] >= card["max_uses"]:
                return -1

            # التحقق مما إذا كان المستخدم قد استعمل مفتاح البطاقة هذا مسبقاً
            cursor.execute(
                "SELECT COUNT(*) as count FROM card_key_usage WHERE key_code = %s AND user_id = %s",
                (key_code, user_id),
            )
            count = cursor.fetchone()
            if count['count'] > 0:
                return -3

            # تحديث عدد مرات الاستخدام
            cursor.execute(
                "UPDATE card_keys SET current_uses = current_uses + 1 WHERE key_code = %s",
                (key_code,),
            )

            # تسجيل سجل الاستخدام
            cursor.execute(
                "INSERT INTO card_key_usage (key_code, user_id, used_at) VALUES (%s, %s, NOW())",
                (key_code, user_id),
            )

            # زيادة نقاط المستخدم
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                (card["balance"], user_id),
            )

            conn.commit()
            return card["balance"]

        except Exception as e:
            logger.error(f"فشل في استخدام مفتاح البطاقة: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def get_card_key_info(self, key_code: str) -> Optional[Dict]:
        """الحصول على معلومات مفتاح البطاقة"""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            cursor.execute("SELECT * FROM card_keys WHERE key_code = %s", (key_code,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def get_all_card_keys(self, created_by: Optional[int] = None) -> List[Dict]:
        """الحصول على جميع مفاتيح البطاقات (يمكن التصفية/الفلترة حسب المنشئ (creator))"""
        conn = self.get_connection()
        cursor = conn.cursor(DictCursor)

        try:
            if created_by:
                cursor.execute(
                    "SELECT * FROM card_keys WHERE created_by = %s ORDER BY created_at DESC",
                    (created_by,),
                )
            else:
                cursor.execute("SELECT * FROM card_keys ORDER BY created_at DESC")
            
            return list(cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    def get_all_user_ids(self) -> List[int]:
        """الحصول على جميع معرّفات (IDs) المستخدمين"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT user_id FROM users")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            cursor.close()
            conn.close()


# إنشاء اسم مستعار (alias) للنسخة العامة، للحفاظ على التوافق مع إصدار SQLite
Database = MySQLDatabase

