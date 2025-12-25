"""
Database Configuration and Connection Management
Brilliox Pro CRM v7.0
"""
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime
import json

from app.core.config import settings
from supabase import create_client, Client


# نوع قاعدة البيانات
DB_TYPE = "postgres" if settings.DATABASE_URL else "local"

# عميل Supabase
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """الحصول على عميل Supabase"""
    global _supabase_client
    if _supabase_client is None:
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                _supabase_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
            except Exception as e:
                print(f"Error connecting to Supabase: {e}")
    return _supabase_client


def init_db():
    """تهيئة قاعدة البيانات"""
    print(f"Initializing database... Type: {DB_TYPE}")

    if settings.DATABASE_URL:
        client = get_supabase_client()
        if client:
            print("Supabase connection established")
    else:
        print("Using local storage (no database configured)")


def get_db():
    """الحصول على اتصال قاعدة البيانات"""
    client = get_supabase_client()
    if client:
        return client
    return None


@contextmanager
def get_db_context():
    """حصول على قاعدة البيانات كسياق"""
    client = get_supabase_client()
    yield client


class LocalStorage:
    """تخزين محلي للمشاريع الصغيرة"""

    def __init__(self):
        self.data_file = "data/local_storage.json"
        self._ensure_file()

    def _ensure_file(self):
        """التأكد من وجود ملف البيانات"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            self._save({})

    def _save(self, data: Dict[str, Any]):
        """حفظ البيانات"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self) -> Dict[str, Any]:
        """تحميل البيانات"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def get(self, table: str, key: str) -> Optional[Dict[str, Any]]:
        """الحصول على عنصر"""
        data = self._load()
        table_data = data.get(table, {})
        return table_data.get(key)

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """الحصول على جميع العناصر من جدول"""
        data = self._load()
        return list(data.get(table, {}).values())

    def insert(self, table: str, key: str, value: Dict[str, Any]) -> str:
        """إضافة عنصر جديد"""
        data = self._load()
        if table not in data:
            data[table] = {}

        value['id'] = key
        value['created_at'] = datetime.now().isoformat()
        data[table][key] = value
        self._save(data)
        return key

    def update(self, table: str, key: str, value: Dict[str, Any]) -> bool:
        """تحديث عنصر"""
        data = self._load()
        if table not in data or key not in data[table]:
            return False

        existing = data[table][key]
        existing.update(value)
        existing['updated_at'] = datetime.now().isoformat()
        data[table][key] = existing
        self._save(data)
        return True

    def delete(self, table: str, key: str) -> bool:
        """حذف عنصر"""
        data = self._load()
        if table not in data or key not in data[table]:
            return False

        del data[table][key]
        self._save(data)
        return True

    def query(self, table: str, **filters) -> List[Dict[str, Any]]:
        """استعلام بسيط"""
        results = []
        for item in self.get_all(table):
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results


# إنشاء تخزين محلي
local_storage = LocalStorage()


class DatabaseOperations:
    """عمليات قاعدة البيانات الموحدة"""

    @staticmethod
    def get_user(username: str) -> Optional[Dict[str, Any]]:
        """الحصول على المستخدم"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('users').select('*').eq('username', username).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Error getting user: {e}")

        # استخدام التخزين المحلي
        return local_storage.get('users', username)

    @staticmethod
    def create_user(username: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء مستخدم جديد"""
        user_data = {
            'username': username,
            'wallet_balance': data.get('wallet_balance', settings.DEFAULT_BALANCE),
            'is_admin': data.get('is_admin', False),
            'password': data.get('password'),
            'created_at': datetime.now().isoformat()
        }

        client = get_supabase_client()
        if client:
            try:
                result = client.table('users').insert(user_data).execute()
                return result.data[0]
            except Exception as e:
                print(f"Error creating user: {e}")

        # استخدام التخزين المحلي
        local_storage.insert('users', username, user_data)
        return user_data

    @staticmethod
    def update_user(username: str, data: Dict[str, Any]) -> bool:
        """تحديث المستخدم"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('users').update(data).eq('username', username).execute()
                return bool(result.data)
            except Exception as e:
                print(f"Error updating user: {e}")

        return local_storage.update('users', username, data)

    @staticmethod
    def add_lead(user_id: str, lead_data: Dict[str, Any]) -> str:
        """إضافة عميل محتمل"""
        import uuid
        lead_id = str(uuid.uuid4())[:8]
        lead_data['user_id'] = user_id
        lead_data['id'] = lead_id
        lead_data['created_at'] = datetime.now().isoformat()

        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').insert(lead_data).execute()
                return result.data[0].get('id', lead_id)
            except Exception as e:
                print(f"Error adding lead: {e}")

        local_storage.insert('leads', lead_id, lead_data)
        return lead_id

    @staticmethod
    def get_leads(user_id: str) -> List[Dict[str, Any]]:
        """الحصول على عملاء المستخدم"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').select('*').eq('user_id', user_id).execute()
                return result.data
            except Exception as e:
                print(f"Error getting leads: {e}")

        return local_storage.query('leads', user_id=user_id)

    @staticmethod
    def get_all_leads() -> List[Dict[str, Any]]:
        """الحصول على جميع العملاء"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').select('*').execute()
                return result.data
            except Exception as e:
                print(f"Error getting all leads: {e}")

        return local_storage.get_all('leads')
