"""
API Routes - All Endpoints
Brilliox Pro CRM v7.0
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from pydantic import BaseModel, field_validator

from app.core.config import settings
from app.core.security import sanitize_input
from app.core.i18n import t
from app.services.user_service import UserService
from app.services.lead_service import LeadService, LeadScorer
from app.services.ai_service import AIService


# إنشاء جهاز التوجيه
router = APIRouter()


# ==================== نماذج البيانات ====================

class ChatRequest(BaseModel):
    """طلب المحادثة"""
    message: str

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('الرسالة فارغة')
        return sanitize_input(v, 5000)


class UserCreate(BaseModel):
    """إنشاء مستخدم"""
    username: str
    password: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """تغيير كلمة المرور"""
    old_password: str
    new_password: str


class AddLeadRequest(BaseModel):
    """إضافة عميل"""
    name: str
    phone: str
    email: Optional[str] = None
    status: str = "new"
    notes: Optional[str] = None


class ImportLeadsRequest(BaseModel):
    """استيراد عملاء"""
    leads: List[dict]


class UpdateLeadRequest(BaseModel):
    """تحديث عميل"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


# ==================== نقاط النهاية ====================

@router.get("/")
async def index():
    """الصفحة الرئيسية"""
    if settings.DEBUG:
        return {
            "app": settings.APP_NAME,
            "version": settings.VERSION,
            "status": "running",
            "docs": "/docs"
        }
    return {"message": "Brilliox Pro CRM API"}


@router.get("/health")
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "version": "7.0.0",
        "app": "Brilliox Pro CRM",
        "database": "local",
        "environment": "test"
    }


@router.get("/api/translations/{lang}")
async def get_translations(lang: str = "ar"):
    """الحصول على الترجمات"""
    from app.core.i18n import get_all_translations, get_direction
    return {
        "translations": get_all_translations(lang),
        "direction": get_direction(lang),
        "lang": lang
    }


# ==================== المصادقة ====================

@router.post("/api/login")
async def login(data: UserCreate):
    """تسجيل الدخول / التسجيل"""
    if data.password:
        user = UserService.login_with_password(data.username, data.password)
        if not user:
            raise HTTPException(status_code=401, detail="اسم المستخدم أو كلمة المرور غير صحيحة")
    else:
        user = UserService.get_or_create(data.username)

    has_password = bool(user.get("password", ""))

    return {
        "success": True,
        "user_id": data.username,
        "wallet_balance": user.get("wallet_balance", settings.DEFAULT_BALANCE),
        "is_admin": user.get("is_admin", False),
        "has_password": has_password
    }


@router.post("/api/user/{user_id}/change-password")
async def change_password(user_id: str, data: ChangePasswordRequest):
    """تغيير كلمة المرور"""
    success, message = UserService.change_password(user_id, data.old_password, data.new_password)

    if success:
        return {"success": True, "message": message}
    raise HTTPException(status_code=400, detail=message)


@router.get("/api/wallet/{user_id}")
async def get_wallet(user_id: str):
    """الحصول على المحفظة"""
    user = UserService.get_or_create(user_id)
    return {
        "user_id": user_id,
        "wallet_balance": user.get("wallet_balance", 0),
        "is_admin": user.get("is_admin", False)
    }


# ==================== المحادثة الذكية ====================

@router.post("/api/chat/{user_id}")
async def chat(user_id: str, data: ChatRequest):
    """المحادثة الذكية"""
    message = data.message.strip()
    is_admin = UserService.is_admin(user_id)

    try:
        result = await AIService.generate_response(
            prompt=message,
            use_cache=True,
            cost=settings.CHAT_COST
        )

        if result.get("success"):
            # خصم الرصيد
            if result.get("tokens_used", 0) > 0:
                UserService.deduct_balance(user_id, result["tokens_used"])

            user = UserService.get_or_create(user_id)
            result["remaining_balance"] = user.get("wallet_balance", 0)

        return result

    except Exception as e:
        print(f"Chat error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "حدث خطأ، حاول مرة أخرى", "tokens_used": 0}
        )


# ==================== إدارة العملاء ====================

@router.get("/api/leads/{user_id}")
async def get_leads(user_id: str, status: Optional[str] = None):
    """الحصول على عملاء المستخدم"""
    leads = LeadService.get_user_leads(user_id)

    if status:
        leads = [l for l in leads if l.get("status") == status]

    return {"leads": leads, "count": len(leads)}


@router.get("/api/leads/{user_id}/scored")
async def get_scored_leads(user_id: str):
    """الحصول على عملاء مع التقييم"""
    leads = LeadService.get_user_leads(user_id)
    scored_leads = LeadScorer.score_leads_batch(leads)
    return {"leads": scored_leads, "count": len(scored_leads)}


@router.get("/api/leads/{user_id}/insights")
async def get_lead_insights(user_id: str):
    """الحصول على رؤى العملاء"""
    leads = LeadService.get_user_leads(user_id)
    return LeadScorer.get_insights(leads)


@router.post("/api/leads/{user_id}/add")
async def add_lead(user_id: str, data: AddLeadRequest):
    """إضافة عميل جديد"""
    lead_data = {
        "name": sanitize_input(data.name),
        "phone": sanitize_input(data.phone),
        "email": sanitize_input(data.email) if data.email else None,
        "status": data.status,
        "notes": sanitize_input(data.notes) if data.notes else None,
        "source": "manual"
    }

    lead_id = LeadService.add_lead(user_id, lead_data)

    return {"success": True, "lead_id": lead_id, "message": "تم إضافة العميل بنجاح"}


@router.post("/api/leads/{user_id}/import")
async def import_leads(user_id: str, data: ImportLeadsRequest):
    """استيراد عملاء"""
    result = LeadService.import_leads(user_id, data.leads)

    return {
        "success": True,
        "imported": result['imported'],
        "message": f"تم استيراد {result['imported']} عميل"
    }


@router.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, data: UpdateLeadRequest):
    """تحديث عميل"""
    updates = {}
    if data.name:
        updates['name'] = sanitize_input(data.name)
    if data.phone:
        updates['phone'] = sanitize_input(data.phone)
    if data.email:
        updates['email'] = sanitize_input(data.email)
    if data.status:
        updates['status'] = data.status
    if data.notes:
        updates['notes'] = sanitize_input(data.notes)

    success = LeadService.update_lead(lead_id, updates)

    if success:
        return {"success": True, "message": "تم التحديث بنجاح"}
    raise HTTPException(status_code=404, detail="العميل غير موجود")


@router.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str):
    """حذف عميل"""
    if LeadService.delete_lead(lead_id):
        return {"success": True, "message": "تم الحذف بنجاح"}
    raise HTTPException(status_code=404, detail="العميل غير موجود")


# ==================== الإحصائيات ====================

@router.get("/api/stats/{user_id}")
async def get_stats(user_id: str):
    """الحصول على الإحصائيات"""
    user = UserService.get_or_create(user_id)
    lead_stats = LeadService.get_lead_stats(user_id)

    return {
        "user_id": user_id,
        "wallet_balance": user.get("wallet_balance", 0),
        "leads": lead_stats
    }


# ==================== Webhooks ====================

@router.post("/webhook/lead")
async def webhook_lead(request_data: dict):
    """استقبال عملاء من الإعلانات"""
    try:
        # استخراج البيانات
        name = request_data.get("name") or request_data.get("full_name") or ""
        phone = request_data.get("phone") or request_data.get("phone_number") or ""
        email = request_data.get("email") or ""
        source = request_data.get("source") or request_data.get("platform") or "ads"
        campaign = request_data.get("campaign") or request_data.get("campaign_name") or ""

        if not name and not phone:
            return {"success": False, "error": "No name or phone"}

        lead_data = {
            "name": sanitize_input(str(name)),
            "phone": sanitize_input(str(phone)),
            "email": sanitize_input(str(email)) if email else None,
            "status": "bait_sent",
            "source": f"ads_{source}",
            "notes": f"Campaign: {campaign}" if campaign else None
        }

        lead_id = LeadService.add_lead("admin", lead_data)

        return {"success": True, "lead_id": lead_id, "message": "Lead received"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/webhook/lead")
async def webhook_verify(mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    """التحقق من Webhook"""
    if mode == "subscribe" and hub_verify_token == "hunter_pro_2024":
        return int(hub_challenge or 0)
    return {"status": "ready"}
