"""
Test Suite - Brilliox Pro CRM v7.0
Comprehensive tests for all system components
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# إضافة المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ==================== Fixtures ====================

@pytest.fixture
def mock_settings():
    """إعدادات الاختبار"""
    with patch('app.core.config.Settings') as mock:
        instance = MagicMock()
        instance.APP_NAME = "Brilliox Pro CRM Test"
        instance.VERSION = "7.0.0"
        instance.DEBUG = True
        instance.ADMIN_USERNAME = "admin"
        instance.ADMIN_PASSWORD = "test"
        instance.DEFAULT_BALANCE = 100
        instance.CHAT_COST = 2
        instance.HUNT_COST = 20
        instance.AD_COST = 15
        instance.CAMPAIGN_COST = 50
        instance.CACHE_TTL = 3600
        instance.RATE_LIMIT_REQUESTS = 60
        instance.RATE_LIMIT_WINDOW = 60
        instance.BLOCK_DURATION = 300
        instance.OPENAI_API_KEY = None
        instance.GOOGLE_API_KEY = None
        instance.ANTHROPIC_API_KEY = None
        instance.GROQ_API_KEY = None
        instance.DATABASE_URL = None
        instance.SUPABASE_URL = None
        instance.SUPABASE_KEY = None
        instance.UPLOAD_DIR = "test_uploads"
        instance.STATIC_DIR = "static"
        instance.TEMPLATES_DIR = "templates"
        instance.DATA_DIR = "data"
        instance.ENVIRONMENT = "test"
        instance.is_ai_available.return_value = False
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_database():
    """قاعدة بيانات الاختبار"""
    with patch('app.core.database.get_supabase_client') as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def client(mock_settings, mock_database):
    """عميل الاختبار"""
    # استيراد بعدpatch
    from app.main import app
    from app.core.security import rate_limit, sanitize_input

    with patch('app.core.security.settings', mock_settings):
        with patch('app.core.config.settings', mock_settings):
            with TestClient(app) as test_client:
                yield test_client


# ==================== Health Tests ====================

class TestHealthEndpoints:
    """اختبارات فحص الصحة"""

    def test_health_check(self, client):
        """فحص صحة النظام"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client):
        """اختبار نقطة الجذر"""
        response = client.get("/")
        assert response.status_code == 200


# ==================== Security Tests ====================

class TestSecurity:
    """اختبارات الأمان"""

    def test_rate_limit(self, mock_settings):
        """اختبار تحديد معدل الطلبات"""
        from app.core.security import SecurityManager

        manager = SecurityManager()

        # طلب مسموح
        allowed, msg = manager.rate_limit("127.0.0.1", max_requests=5, window=60)
        assert allowed is True

        # تجاوز الحد
        for _ in range(5):
            manager.rate_limit("127.0.0.1", max_requests=5, window=60)

        allowed, msg = manager.rate_limit("127.0.0.1", max_requests=5, window=60)
        assert allowed is False
        assert "محظور" in msg or "blocked" in msg.lower()

    def test_sanitize_input(self, mock_settings):
        """اختبار تنظيف المدخلات"""
        from app.core.security import SecurityManager

        manager = SecurityManager()

        # النص العادي
        clean = manager.sanitize_input("مرحباً بالعالم")
        assert clean == "مرحباً بالعالم"

        # النص مع أكواد خبيثة
        dirty = '<script>alert("xss")</script>مرحباً'
        clean = manager.sanitize_input(dirty)
        assert "<script>" not in clean
        assert "alert" not in clean

        # التحقق من الإرجاع
        assert "مرحباً" in clean

    def test_validate_password(self, mock_settings):
        """اختبار التحقق من كلمة المرور"""
        from app.core.security import SecurityManager

        manager = SecurityManager()

        # كلمة مرور قصيرة
        valid, msg = manager.validate_password("123")
        assert valid is False

        # كلمة مرور صالحة
        valid, msg = manager.validate_password("1234")
        assert valid is True


# ==================== User Service Tests ====================

class TestUserService:
    """اختبارات خدمة المستخدمين"""

    def test_get_or_create_user(self, mock_settings, mock_database):
        """اختبار إنشاء مستخدم"""
        from app.services.user_service import UserService

        with patch('app.services.user_service.get_supabase_client', return_value=None):
            with patch('app.services.user_service.DatabaseOperations') as mock_db:
                mock_db.get_user.return_value = None
                mock_db.create_user.return_value = {
                    "username": "test_user",
                    "wallet_balance": 100,
                    "is_admin": False
                }

                user = UserService.get_or_create("test_user")

                assert user["username"] == "test_user"
                assert user["wallet_balance"] == 100

    def test_is_admin(self, mock_settings):
        """اختبار صلاحيات الأدمن"""
        from app.services.user_service import UserService
        from app.core.security import security_manager

        # يجب أن يكون الأدمن أدمن
        assert security_manager.is_admin("admin") is True

        # مستخدم عادي
        assert security_manager.is_admin("regular_user") is False


# ==================== Lead Service Tests ====================

class TestLeadService:
    """اختبارات خدمة العملاء"""

    def test_add_lead(self, mock_settings, mock_database):
        """اختبار إضافة عميل"""
        from app.services.lead_service import LeadService

        with patch('app.services.lead_service.get_supabase_client', return_value=None):
            with patch('app.services.lead_service.DatabaseOperations') as mock_db:
                mock_db.add_lead.return_value = "lead_123"

                lead_id = LeadService.add_lead("user1", {
                    "name": "عميل جديد",
                    "phone": "0123456789"
                })

                assert lead_id == "lead_123"

    def test_get_leads(self, mock_settings, mock_database):
        """اختبار الحصول على العملاء"""
        from app.services.lead_service import LeadService

        with patch('app.services.lead_service.get_supabase_client', return_value=None):
            with patch('app.services.lead_service.DatabaseOperations') as mock_db:
                mock_db.get_leads.return_value = [
                    {"id": "1", "name": "عميل 1"},
                    {"id": "2", "name": "عميل 2"}
                ]

                leads = LeadService.get_user_leads("user1")

                assert len(leads) == 2
                assert leads[0]["name"] == "عميل 1"


# ==================== Lead Scoring Tests ====================

class TestLeadScoring:
    """اختبارات تقييم العملاء"""

    def test_calculate_score_basic(self, mock_settings):
        """اختبار حساب الدرجة الأساسي"""
        from app.services.lead_service import LeadScorer

        lead = {
            "name": "عميل",
            "phone": "0123456789",
            "status": "new"
        }

        result = LeadScorer.calculate_score(lead)

        assert "score" in result
        assert "grade" in result
        assert "factors" in result
        assert result["score"] > 0

    def test_get_grade(self, mock_settings):
        """اختبار التقديرات"""
        from app.services.lead_service import LeadScorer

        assert LeadScorer._get_grade(95) == "ممتاز"
        assert LeadScorer._get_grade(80) == "جيد جداً"
        assert LeadScorer._get_grade(60) == "جيد"
        assert LeadScorer._get_grade(40) == "متوسط"
        assert LeadScorer._get_grade(20) == "ضعيف"

    def test_score_leads_batch(self, mock_settings):
        """اختبار تقييم مجموعة عملاء"""
        from app.services.lead_service import LeadScorer

        leads = [
            {"name": "عميل 1", "phone": "0123456789", "status": "hot"},
            {"name": "عميل 2", "phone": "0123456788", "status": "new"}
        ]

        scored = LeadScorer.score_leads_batch(leads)

        assert len(scored) == 2
        assert "score" in scored[0]
        assert "grade" in scored[0]


# ==================== AI Service Tests ====================

class TestAIService:
    """اختبارات خدمة الذكاء الاصطناعي"""

    def test_cache_key_generation(self, mock_settings):
        """اختبار توليد مفتاح التخزين المؤقت"""
        from app.services.ai_service import get_cache_key

        key1 = get_cache_key("اختبار", "نظام")
        key2 = get_cache_key("اختبار", "نظام")
        key3 = get_cache_key("مختلف", "نظام")

        assert key1 == key2
        assert key1 != key3

    def test_generate_response_no_ai(self, mock_settings):
        """اختبار الاستجابة بدون ذكاء اصطناعي"""
        import asyncio
        from app.services.ai_service import AIService

        with patch('app.services.ai_service.AIService.call_openai', return_value=None):
            with patch('app.services.ai_service.AIService.call_gemini', return_value=None):
                with patch('app.services.ai_service.AIService.call_anthropic', return_value=None):
                    with patch('app.services.ai_service.AIService.call_groq', return_value=None):
                        result = asyncio.run(
                            AIService.generate_response("اختبار")
                        )

                        assert result["success"] is False
                        assert "error" in result


# ==================== i18n Tests ====================

class TestInternationalization:
    """اختبارات الترجمة"""

    def test_translation_function(self, mock_settings):
        """اختبار دالة الترجمة"""
        from app.core.i18n import t

        # يجب أن تعمل الترجمة
        result = t("app_name")
        assert "Brilliox" in result or "app_name" == result

    def test_get_direction(self, mock_settings):
        """اختبار اتجاه النص"""
        from app.core.i18n import get_direction

        assert get_direction("ar") == "rtl"
        assert get_direction("en") == "ltr"


# ==================== Event System Tests ====================

class TestEventSystem:
    """اختبارات نظام الأحداث"""

    def test_system_events(self, mock_settings):
        """اختبار أنواع الأحداث"""
        from app.core.events import SystemEvent

        assert SystemEvent.LEAD_ADDED.value == "lead_added"
        assert SystemEvent.CHAT_MESSAGE.value == "chat_message"
        assert SystemEvent.SYSTEM_READY.value == "system_ready"

    def test_unified_system(self, mock_settings):
        """اختبار النظام الموحد"""
        from app.core.events import UnifiedSystem

        # إنشاء نظام جديد
        system = UnifiedSystem()
        system.initialize()

        # التحقق من التهيئة
        assert system.get_state()["version"] == "7.0.0"

    def test_emit_event(self, mock_settings):
        """اختبار إرسال الأحداث"""
        from app.core.events import UnifiedSystem, SystemEvent

        system = UnifiedSystem()
        system.initialize()

        # تسجيل مستمع
        received = []
        @system.on(SystemEvent.LEAD_ADDED)
        def handler(event, data):
            received.append(data)

        # إرسال حدث
        system.emit(SystemEvent.LEAD_ADDED, {"lead_id": "123"})

        # التحقق من الاستلام
        assert len(received) == 1
        assert received[0]["lead_id"] == "123"


# ==================== CRM Tests ====================

class TestCRM:
    """اختبارات CRM"""

    def test_crm_stats(self, mock_settings, mock_database):
        """اختبار إحصائيات CRM"""
        from main_crm import CRMStats

        with patch('main_crm.LeadService') as mock_leads:
            with patch('main_crm.UserService') as mock_users:
                mock_leads.get_all_leads.return_value = []
                mock_leads.get_user_leads.return_value = []
                mock_users.get_all_users.return_value = []
                mock_users.get_or_create.return_value = {"wallet_balance": 100}

                stats = CRMStats.get_overall_stats()

                assert "total_leads" in stats
                assert "conversion_rate" in stats

    def test_funnel_analysis(self, mock_settings, mock_database):
        """اختبار تحليل قمع المبيعات"""
        from main_crm import CRMAnalytics

        with patch('main_crm.LeadService') as mock_leads:
            mock_leads.get_all_leads.return_value = []

            result = CRMAnalytics.get_funnel_analysis()

            assert "funnel" in result
            assert "total_leads" in result


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
