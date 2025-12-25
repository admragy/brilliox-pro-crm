# Brilliox Pro CRM v7.0

<div align="center">

![Brilliox Pro CRM](https://img.shields.io/badge/Brilliox-Pro%20CRM-v7.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**نظام إدارة علاقات العملاء الذكي المدعوم بالذكاء الاصطناعي**

[English](README.md) | [العربية](README_AR.md)

</div>

---

## المميزات الرئيسية

### 🤖 ذكاء اصطناعي متقدم
- **محادثة ذكية**: دردشة مع ذكاء اصطناعي يفهم احتياجاتك ويقدم حلولاً مخصصة
- **اصطياد العملاء**: توليد استراتيجيات بحث ذكية لإيجاد عملاء محتملين
- **إنشاء الإعلانات**: كتابة محتوى إعلاني احترافي لمنصات متعددة
- **تقييم العملاء**: تحليل وتقييم العملاء المحتملين تلقائياً

### 📊 إدارة متكاملة للعملاء
- إضافة وتعديل وحذف العملاء
- تتبع مراحل قمع المبيعات
- استيراد وتصدير البيانات
- مشاركة العملاء بين المستخدمين

### 🌐 دعم متعدد اللغات
- دعم كامل للغة العربية (RTL)
- دعم اللغة الإنجليزية
- واجهة مستخدم سهلة ومريحة

### 📱 دعم تطبيقات الويب التقدمية (PWA)
- تثبيت التطبيق على الأجهزة
- تجربة تطبيق أصلية
- دعم وضع عدم الاتصال

### 🔒 أمان متقدم
- تحديد معدل الطلبات
- تنظيف المدخلات
- تشفير كلمات المرور
- صلاحيات الأدمن

---

## المتطلبات

- Python 3.10 أو أحدث
- PostgreSQL (اختياري)
- Supabase (اختياري)
- Redis (اختياري للـ caching)

---

## التثبيت

### ١. استنساخ المشروع

```bash
git clone https://github.com/yourusername/brilliox-pro-crm.git
cd brilliox-pro-crm
```

### ٢. إنشاء بيئة افتراضية

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows
```

### ٣. تثبيت التبعيات

```bash
pip install -r requirements.txt
```

### ٤. إعداد متغيرات البيئة

```bash
cp .env.example .env
# تعديل ملف .env بالمتغيرات المطلوبة
```

### ٥. تشغيل التطبيق

```bash
python main.py
```

أو باستخدام Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

---

## متغيرات البيئة

```env
# التطبيق
DEBUG=true
ENVIRONMENT=development

# قاعدة البيانات
DATABASE_URL=postgresql://user:pass@localhost:5432/brilliox
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key

# الذكاء الاصطناعي
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant...
GROQ_API_KEY=gsk_...

# الأمان
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
JWT_SECRET_KEY=your-jwt-secret

# الإعدادات
CACHE_TTL=3600
DEFAULT_BALANCE=100
```

---

## النشر

### باستخدام Docker

```bash
docker-compose up -d
```

### على Fly.io

```bash
fly deploy
```

### على Vercel

```bash
vercel deploy
```

---

## واجهة برمجة التطبيقات (API)

### المصادقة

```python
POST /api/login
{
    "username": "user",
    "password": "pass"  # اختياري
}
```

### المحادثة الذكية

```python
POST /api/chat/{user_id}
{
    "message": "أريد إعلانات لمطعم"
}
```

### العملاء

```python
GET  /api/leads/{user_id}           # الحصول على العملاء
POST /api/leads/{user_id}/add       # إضافة عميل
GET  /api/leads/{user_id}/scored    # العملاء مع التقييم
POST /api/leads/{user_id}/import    # استيراد عملاء
```

### الإحصائيات

```python
GET /api/stats/{user_id}
GET /health
```

---

## هيكل المشروع

```
brilliox-unified/
├── main.py                 # نقطة الدخول الرئيسية
├── main_crm.py            # وظائف CRM
├── test_hunter_pro.py     # الاختبارات
├── requirements.txt       # التبعيات
├── app/
│   ├── __init__.py
│   ├── main.py           # تهيئة التطبيق
│   ├── router.py         # نقاط النهاية
│   ├── core/
│   │   ├── config.py     # الإعدادات
│   │   ├── database.py   # قاعدة البيانات
│   │   ├── security.py   # الأمان
│   │   ├── i18n.py       # الترجمة
│   │   └── events.py     # نظام الأحداث
│   ├── services/
│   │   ├── ai_service.py    # الذكاء الاصطناعي
│   │   ├── user_service.py  # المستخدمين
│   │   └── lead_service.py  # العملاء
├── static/
│   └── manifest.json    # PWA
├── templates/
│   └── index.html
└── locales/
    ├── ar.json
    └── en.json
```

---

## الاختبارات

```bash
pytest test_hunter_pro.py -v
```

---

## المساهمة

نرحب بمساهماتكم! يرجى قراءة [CONTRIBUTING.md](CONTRIBUTING.md) للمزيد من التفاصيل.

---

## الترخيص

هذا المشروع مرخص تحت MIT License - راجع [LICENSE](LICENSE) للمزيد من المعلومات.

---

## التواصل

- الموقع: https://brilliox.com
- البريد: support@brilliox.com
- GitHub: https://github.com/brilliox

---

<div align="center">

**تم التطوير بـ ❤️ بواسطة فريق Brilliox**

</div>
