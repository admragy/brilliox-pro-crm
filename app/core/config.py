"""
Centralized Configuration Settings
Brilliox Pro CRM - Unified System
"""
import os
from dataclasses import dataclass, field
from typing import Optional, List
from functools import lru_cache


@dataclass
class Settings:
    """إعدادات النظام المركزية"""

    # Application
    APP_NAME: str = "Brilliox Pro CRM"
    APP_VERSION: str = "7.0.0"
    VERSION: str = "7.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = "uploads"
    STATIC_DIR: str = "static"
    TEMPLATES_DIR: str = "templates"
    DATA_DIR: str = "data"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "5000"))

    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DB_TYPE: str = "postgres" if os.getenv("DATABASE_URL") else "local"

    # Supabase Configuration
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")

    # AI APIs Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")

    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Search APIs
    SERPER_API_KEY: Optional[str] = None
    SERPER_KEYS: List[str] = field(default_factory=list)

    # Payment Gateways
    PAYMOB_API_KEY: Optional[str] = os.getenv("PAYMOB_API_KEY")
    PAYMOB_INTEGRATION_ID: Optional[str] = os.getenv("PAYMOB_INTEGRATION_ID")
    PAYMOB_IFRAME_ID: Optional[str] = os.getenv("PAYMOB_IFRAME_ID")
    PAYMOB_HMAC_SECRET: Optional[str] = os.getenv("PAYMOB_HMAC_SECRET")

    # WhatsApp Integration
    WHATSAPP_API_KEY: Optional[str] = os.getenv("WHATSAPP_API_KEY")
    WHATSAPP_PHONE_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_ID")

    # Meta Ads Integration
    META_ACCESS_TOKEN: Optional[str] = os.getenv("META_ACCESS_TOKEN")
    META_AD_ACCOUNT_ID: Optional[str] = os.getenv("META_AD_ACCOUNT_ID")
    META_APP_ID: Optional[str] = os.getenv("META_APP_ID")
    META_APP_SECRET: Optional[str] = os.getenv("META_APP_SECRET")

    # Security Configuration
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "P@$$w0rd@1982")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    BLOCK_DURATION: int = int(os.getenv("BLOCK_DURATION", "300"))

    # Token Costs
    CHAT_COST: int = int(os.getenv("CHAT_COST", "2"))
    HUNT_COST: int = int(os.getenv("HUNT_COST", "20"))
    AD_COST: int = int(os.getenv("AD_COST", "15"))
    CAMPAIGN_COST: int = int(os.getenv("CAMPAIGN_COST", "50"))
    DEFAULT_BALANCE: int = int(os.getenv("DEFAULT_BALANCE", "100"))

    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Language Configuration
    DEFAULT_LANGUAGE: str = "ar"
    SUPPORTED_LANGUAGES: List[str] = field(default_factory=lambda: ["ar", "en"])

    # PWA Configuration
    PWA_NAME: str = "Brilliox Pro CRM"
    PWA_SHORT_NAME: str = "Brilliox"
    PWA_THEME_COLOR: str = "#0f172a"
    PWA_BACKGROUND_COLOR: str = "#0f172a"
    PWA_DISPLAY: str = "standalone"

    def __post_init__(self):
        """معالجة ما بعد التهيئة"""
        # تحويل SERPER_KEYS من متغير البيئة
        serper_keys_env = os.getenv("SERPER_KEYS", "")
        if serper_keys_env:
            self.SERPER_KEYS = [k.strip() for k in serper_keys_env.split(",") if k.strip()]
            if self.SERPER_KEYS:
                self.SERPER_API_KEY = self.SERPER_KEYS[0]

        # التأكد من وجود المجلدات
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(os.path.join(self.STATIC_DIR, "css"), exist_ok=True)
        os.makedirs(os.path.join(self.STATIC_DIR, "js"), exist_ok=True)
        os.makedirs(os.path.join(self.STATIC_DIR, "images"), exist_ok=True)
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def get_database_url(self) -> str:
        """الحصول على عنوان قاعدة البيانات"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://postgres:postgres@localhost:5432/brilliox"

    def is_ai_available(self) -> bool:
        """التحقق من توفر أي خدمة ذكاء اصطناعي"""
        return any([
            self.OPENAI_API_KEY,
            self.GOOGLE_API_KEY,
            self.ANTHROPIC_API_KEY,
            self.GROQ_API_KEY
        ])


@lru_cache()
def get_settings() -> Settings:
    """الحصول على إعدادات النظام (مع تخزين مؤقت)"""
    return Settings()


settings = get_settings()
