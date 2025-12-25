"""
User Service - User Management and Authentication
Brilliox Pro CRM v7.0
"""
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.core.security import security_manager
from app.core.database import DatabaseOperations


class UserService:
    """خدمة إدارة المستخدمين"""

    @staticmethod
    def get_or_create(username: str) -> Dict[str, Any]:
        """
        الحصول على مستخدم أو إنشاؤه إذا لم يكن موجوداً

        Args:
            username: اسم المستخدم

        Returns:
            Dict: بيانات المستخدم
        """
        user = DatabaseOperations.get_user(username)

        if not user:
            user = DatabaseOperations.create_user(username, {
                'wallet_balance': settings.DEFAULT_BALANCE,
                'is_admin': False
            })

        return user

    @staticmethod
    def login_with_password(username: str, password: str) -> Optional[Dict[str, Any]]:
        """تسجيل الدخول بكلمة مرور"""
        user = DatabaseOperations.get_user(username)

        if user and user.get('password'):
            if security_manager.verify_password(password, user['password']):
                return user

        return None

    @staticmethod
    def change_password(username: str, old_password: str, new_password: str) -> tuple:
        """تغيير كلمة المرور"""
        # التحقق من كلمة المرور القديمة
        user = DatabaseOperations.get_user(username)

        if not user:
            return False, "المستخدم غير موجود"

        if user.get('password'):
            if not security_manager.verify_password(old_password, user['password']):
                return False, "كلمة المرور القديمة غير صحيحة"

        # التحقق من قوة كلمة المرور الجديدة
        valid, msg = security_manager.validate_password(new_password)
        if not valid:
            return False, msg

        # تحديث كلمة المرور
        hashed = security_manager.hash_password(new_password)
        DatabaseOperations.update_user(username, {'password': hashed})

        return True, "تم تغيير كلمة المرور بنجاح"

    @staticmethod
    def set_password(username: str, new_password: str) -> bool:
        """تعيين كلمة مرور جديدة"""
        valid, msg = security_manager.validate_password(new_password)
        if not valid:
            return False

        hashed = security_manager.hash_password(new_password)
        return DatabaseOperations.update_user(username, {'password': hashed})

    @staticmethod
    def is_admin(username: str) -> bool:
        """التحقق من صلاحيات الأدمن"""
        return security_manager.is_admin(username)

    @staticmethod
    def get_wallet_balance(username: str) -> int:
        """الحصول على رصيد المحفظة"""
        user = UserService.get_or_create(username)
        return user.get('wallet_balance', 0)

    @staticmethod
    def update_balance(username: str, amount: int) -> bool:
        """تحديث الرصيد"""
        current = UserService.get_wallet_balance(username)
        new_balance = current + amount

        if new_balance < 0:
            return False

        return DatabaseOperations.update_user(username, {'wallet_balance': new_balance})

    @staticmethod
    def deduct_balance(username: str, amount: int) -> tuple:
        """خصم من الرصيد"""
        current = UserService.get_wallet_balance(username)

        if current < amount:
            return False, "رصيد غير كافي"

        return UserService.update_balance(username, -amount), "تم الخصم"

    @staticmethod
    def get_all_users() -> list:
        """الحصول على جميع المستخدمين"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('users').select('*').execute()
                return result.data
            except Exception as e:
                print(f"Error getting users: {e}")

        return []

    @staticmethod
    def delete_user(username: str) -> bool:
        """حذف مستخدم"""
        # لا يمكن حذف الأدمن
        if username.lower() == settings.ADMIN_USERNAME.lower():
            return False

        return False  # للتعليق لاحقاً


def get_supabase_client():
    """استيراد عميل Supabase"""
    from app.core.database import get_supabase_client
    return get_supabase_client()
