"""
Internationalization Module - Multi-language Support
Brilliox Pro CRM v7.0
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path


# الترجمات المحملة
_translations: Dict[str, Dict[str, str]] = {}


def load_translations():
    """تحميل جميع الترجمات"""
    global _translations

    locales_dir = Path("locales")

    if not locales_dir.exists():
        locales_dir.mkdir(exist_ok=True)
        # إنشاء ملفات الترجمة الافتراضية
        create_default_translations(locales_dir)

    for lang_file in locales_dir.glob("*.json"):
        try:
            lang_code = lang_file.stem
            with open(lang_file, 'r', encoding='utf-8') as f:
                _translations[lang_code] = json.load(f)
        except Exception as e:
            print(f"Error loading translations for {lang_file.stem}: {e}")


def create_default_translations(locales_dir: Path):
    """إنشاء ملفات الترجمة الافتراضية"""

    # الترجمة العربية
    ar_translations = {
        # General
        "app_name": "Brilliox Pro CRM",
        "welcome": "مرحباً بك",
        "login": "تسجيل الدخول",
        "logout": "تسجيل خروج",
        "register": "التسجيل",
        "save": "حفظ",
        "cancel": "إلغاء",
        "delete": "حذف",
        "edit": "تعديل",
        "add": "إضافة",
        "search": "بحث",
        "loading": "جاري التحميل...",
        "error": "حدث خطأ",
        "success": "نجح",
        "confirm": "تأكيد",

        # Navigation
        "dashboard": "لوحة التحكم",
        "leads": "العملاء المحتملين",
        "campaigns": "الحملات",
        "analytics": "التحليلات",
        "settings": "الإعدادات",
        "help": "المساعدة",

        # Lead Management
        "new_lead": "عميل جديد",
        "lead_name": "اسم العميل",
        "lead_phone": "رقم الهاتف",
        "lead_email": "البريد الإلكتروني",
        "lead_status": "حالة العميل",
        "lead_notes": "ملاحظات",
        "lead_source": "مصدر العميل",
        "import_leads": "استيراد العملاء",
        "export_leads": "تصدير العملاء",

        # Lead Status
        "status_new": "جديد",
        "status_bait_sent": "أُرسل الطعم",
        "status_replied": "ردود",
        "status_interested": "مهتم",
        "status_negotiating": "مفاوضات",
        "status_hot": "ساخن",
        "status_closed": "مغلق",
        "status_lost": "فائت",

        # AI Chat
        "ai_chat": "المحادثة الذكية",
        "ai_hint": "اطلب ما تحتاجه... سأجد لك العملاء أو أكتب لك إعلانات",
        "send_message": "إرسال",
        "tokens_used": "العملات المستخدمة",

        # Wallet
        "wallet": "المحفظة",
        "balance": "الرصيد",
        "tokens": "عملات",
        "recharge": "إعادة تعبئة",
        "cost": "التكلفة",

        # Errors
        "error_empty_message": "الرسالة فارغة",
        "error_login_failed": "فشل تسجيل الدخول",
        "error_lead_not_found": "العميل غير موجود",
        "error_not_authorized": "غير مصرح لك",
        "error_server_error": "خطأ في الخادم",

        # Admin
        "admin_panel": "لوحة الإدارة",
        "users": "المستخدمون",
        "system_status": "حالة النظام",
        "all_leads": "جميع العملاء",

        # PWA
        "pwa_install": "تثبيت التطبيق",
        "pwa_installed": "تم التثبيت",

        # Actions
        "action_hunt": "اصطياد عملاء",
        "action_ad": "إنشاء إعلان",
        "action_analyze": "تحليل",
        "action_optimize": "تحسين"
    }

    # الترجمة الإنجليزية
    en_translations = {
        # General
        "app_name": "Brilliox Pro CRM",
        "welcome": "Welcome",
        "login": "Login",
        "logout": "Logout",
        "register": "Register",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "search": "Search",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "confirm": "Confirm",

        # Navigation
        "dashboard": "Dashboard",
        "leads": "Leads",
        "campaigns": "Campaigns",
        "analytics": "Analytics",
        "settings": "Settings",
        "help": "Help",

        # Lead Management
        "new_lead": "New Lead",
        "lead_name": "Lead Name",
        "lead_phone": "Phone Number",
        "lead_email": "Email",
        "lead_status": "Status",
        "lead_notes": "Notes",
        "lead_source": "Source",
        "import_leads": "Import Leads",
        "export_leads": "Export Leads",

        # Lead Status
        "status_new": "New",
        "status_bait_sent": "Bait Sent",
        "status_replied": "Replied",
        "status_interested": "Interested",
        "status_negotiating": "Negotiating",
        "status_hot": "Hot",
        "status_closed": "Closed",
        "status_lost": "Lost",

        # AI Chat
        "ai_chat": "AI Chat",
        "ai_hint": "Ask for what you need... I'll find customers or write ads for you",
        "send_message": "Send",
        "tokens_used": "Tokens Used",

        # Wallet
        "wallet": "Wallet",
        "balance": "Balance",
        "tokens": "Tokens",
        "recharge": "Recharge",
        "cost": "Cost",

        # Errors
        "error_empty_message": "Message is empty",
        "error_login_failed": "Login failed",
        "error_lead_not_found": "Lead not found",
        "error_not_authorized": "Not authorized",
        "error_server_error": "Server error",

        # Admin
        "admin_panel": "Admin Panel",
        "users": "Users",
        "system_status": "System Status",
        "all_leads": "All Leads",

        # PWA
        "pwa_install": "Install App",
        "pwa_installed": "Installed",

        # Actions
        "action_hunt": "Hunt Customers",
        "action_ad": "Create Ad",
        "action_analyze": "Analyze",
        "action_optimize": "Optimize"
    }

    # حفظ الملفات
    with open(locales_dir / "ar.json", 'w', encoding='utf-8') as f:
        json.dump(ar_translations, f, ensure_ascii=False, indent=2)

    with open(locales_dir / "en.json", 'w', encoding='utf-8') as f:
        json.dump(en_translations, f, ensure_ascii=False, indent=2)


def t(key: str, lang: str = "ar") -> str:
    """
    الحصول على الترجمة

    Args:
        key: مفتاح الترجمة
        lang: كود اللغة

    Returns:
        str: النص المترجم أو المفتاح إذا لم يوجد
    """
    if not _translations:
        load_translations()

    # محاولة الحصول على الترجمة
    lang_translations = _translations.get(lang, {})
    if key in lang_translations:
        return lang_translations[key]

    # محاولة اللغة الإنجليزية كاحتياطي
    en_translations = _translations.get("en", {})
    if key in en_translations:
        return en_translations[key]

    return key


def get_all_translations(lang: str) -> Dict[str, str]:
    """الحصول على جميع الترجمات بلغة معينة"""
    if not _translations:
        load_translations()

    return _translations.get(lang, {})


def get_direction(lang: str) -> str:
    """الحصول على اتجاه النص للغة"""
    rtl_languages = ["ar", "he", "fa", "ur"]
    return "rtl" if lang in rtl_languages else "ltr"


def get_supported_languages() -> list:
    """الحصول على اللغات المدعومة"""
    if not _translations:
        load_translations()

    return list(_translations.keys())


# تحميل الترجمات عند استيراد الوحدة
load_translations()
