"""
Security Module - Rate Limiting and Input Sanitization
Brilliox Pro CRM v7.0
"""
import time
import re
import html
from typing import Tuple, Dict, Any
from collections import defaultdict
import hashlib

from app.core.config import settings


class SecurityManager:
    """مدير الأمان للنظام"""

    def __init__(self):
        self._rate_limit_store: Dict[str, Dict[str, Any]] = {}
        self._blocked_ips: Dict[str, float] = {}
        self._failed_attempts: defaultdict = defaultdict(int)

    def rate_limit(self, client_ip: str, max_requests: int = 60, window: int = 60, block_duration: int = 300) -> Tuple[bool, str]:
        """
        تطبيق تحديد معدل الطلبات

        Args:
            client_ip: عنوان IP للعميل
            max_requests: الحد الأقصى للطلبات
            window: نافذة الوقت بالثواني
            block_duration: مدة الحظر بالثواني

        Returns:
            Tuple[bool, str]: (مسموح, رسالة)
        """
        current_time = time.time()

        # التحقق من حظر IP
        if client_ip in self._blocked_ips:
            if current_time - self._blocked_ips[client_ip] < block_duration:
                remaining = int(block_duration - (current_time - self._blocked_ips[client_ip]))
                return False, f"محظور. حاول بعد {remaining} ثانية"
            else:
                del self._blocked_ips[client_ip]

        # تهيئة أو تحديث سجل IP
        if client_ip not in self._rate_limit_store:
            self._rate_limit_store[client_ip] = {
                'requests': [],
                'blocked': False
            }

        client_data = self._rate_limit_store[client_ip]

        # إزالة الطلبات القديمة من النافذة
        client_data['requests'] = [
            req_time for req_time in client_data['requests']
            if current_time - req_time < window
        ]

        # التحقق من الحد
        if len(client_data['requests']) >= max_requests:
            # حظر IP
            self._blocked_ips[client_ip] = current_time
            client_data['blocked'] = True
            return False, f"تم حظر عنوان IP مؤقتاً بسبب تجاوز الحد"

        # إضافة الطلب الحالي
        client_data['requests'].append(current_time)
        return True, "OK"

    def sanitize_input(self, text: str, max_len: int = 2000) -> str:
        """
        تنظيف المدخلات من الأكواد الخبيثة

        Args:
            text: النص المراد تنظيفه
            max_len: الحد الأقصى لطول النص

        Returns:
            str: النص المنظف
        """
        if not text:
            return ""

        # تحويل إلى نص وتطبيق الحد
        text = html.escape(str(text)[:max_len])

        # إزالة أكواد JavaScript
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)

        # إزالة الأحداث inline
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=\s*[^\s>]+', '', text, flags=re.IGNORECASE)

        # إزالة javascript: URLs
        text = re.sub(r'javascript:[^\s<>"\']*', '', text, flags=re.IGNORECASE)

        # إزالة data: URLs الخطيرة
        text = re.sub(r'data:[^<>]*text/html[^<>]*', '', text, flags=re.IGNORECASE)

        return text.strip()

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        التحقق من قوة كلمة المرور

        Args:
            password: كلمة المرور

        Returns:
            Tuple[bool, str]: (صحيحة, رسالة)
        """
        if len(password) < 4:
            return False, "كلمة المرور يجب أن تكون 4 أحرف على الأقل"

        if len(password) > 128:
            return False, "كلمة المرور طويلة جداً"

        return True, "OK"

    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed: str) -> bool:
        """التحقق من كلمة المرور"""
        return self.hash_password(password) == hashed

    def get_client_ip(self, request) -> str:
        """الحصول على عنوان IP للعميل"""
        # محاولة الحصول على IP الحقيقي من_headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def is_admin(self, username: str) -> bool:
        """التحقق من صلاحيات الأدمن"""
        return username.lower() == settings.ADMIN_USERNAME.lower()


# إنشاء مدير أمان واحد
security_manager = SecurityManager()


def rate_limit(client_ip: str) -> Tuple[bool, str]:
    """دالة تحديد معدل الطلبات"""
    return security_manager.rate_limit(
        client_ip,
        max_requests=settings.RATE_LIMIT_REQUESTS,
        window=settings.RATE_LIMIT_WINDOW,
        block_duration=settings.BLOCK_DURATION
    )


def sanitize_input(text: str, max_len: int = 2000) -> str:
    """دالة تنظيف المدخلات"""
    return security_manager.sanitize_input(text, max_len)


def is_admin(username: str) -> bool:
    """دالة التحقق من الأدمن"""
    return security_manager.is_admin(username)


def validate_password(password: str) -> Tuple[bool, str]:
    """دالة التحقق من كلمة المرور"""
    return security_manager.validate_password(password)
