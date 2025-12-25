"""
Main Application Entry Point
Brilliox Pro CRM v7.0
"""
import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.security import rate_limit
from app.core.events import unified_system, SystemEvent
from app.router import router


# ==================== Middleware ====================

class SecurityMiddleware(BaseHTTPMiddleware):
    """MiddleWare للأمان"""

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        allowed, msg = rate_limit(client_ip)

        if not allowed:
            return JSONResponse({"error": msg}, status_code=429)

        response = await call_next(request)

        # إضافة رؤوس الأمان
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        return response


# ==================== إنشاء التطبيق ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="نظام إدارة علاقات العملاء الذكي",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None
)


# ==================== إضافة Middleware ====================

app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ==================== إنشاء المجلدات ====================

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(settings.STATIC_DIR, "js"), exist_ok=True)
os.makedirs(os.path.join(settings.STATIC_DIR, "images"), exist_ok=True)


# ==================== ربط التوجيهات ====================

app.include_router(router, prefix="")


# ==================== الملفات الثابتة ====================

if os.path.exists(settings.STATIC_DIR):
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


# ==================== الصفحة الرئيسية ====================

@app.get("/index", response_class=HTMLResponse)
async def index_page():
    """الصفحة الرئيسية"""
    if os.path.exists("templates/index.html"):
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    # صفحة افتراضية
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brilliox Pro CRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Cairo', sans-serif; }
        body { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%); min-height: 100vh; }
        .glass { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        .gold { color: #fbbf24; }
    </style>
</head>
<body class="text-white">
    <div class="container mx-auto px-4 py-8">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold gold mb-2">🎯 Brilliox Pro CRM</h1>
            <p class="text-gray-400">نظام الذكاء الاصطناعي لاصطياد العملاء</p>
        </div>

        <div class="glass rounded-2xl p-6 max-w-md mx-auto text-center">
            <p class="text-gray-300 mb-4">النظام يعمل بنجاح!</p>
            <a href="/docs" class="inline-block bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold py-3 px-6 rounded-lg">
                📚 توثيق API
            </a>
        </div>
    </div>
</body>
</html>
    """)


@app.get("/", response_class=HTMLResponse)
async def root():
    """إعادة التوجيه للصفحة الرئيسية"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=/index">
    <title>Brilliox Pro CRM</title>
</head>
<body>
    <p>جاري التوجيه...</p>
</body>
</html>
    """)


# ==================== الأحداث ====================

@app.on_event("startup")
async def startup_event():
    """تشغيل عند بدء التطبيق"""
    print("Starting Brilliox Pro CRM v7.0...")

    # تهيئة قاعدة البيانات
    init_db()

    # تهيئة النظام الموحد
    unified_system.initialize()

    print("System ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """إيقاف عند إغلاق التطبيق"""
    print("Shutting down...")

    if unified_system:
        unified_system.emit(SystemEvent.SYSTEM_SHUTDOWN, {"time": "shutdown"})


# ==================== تشغيل التطبيق ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
