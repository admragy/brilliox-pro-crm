"""
AI Service - Hybrid AI Engine with Multiple Provider Fallback
Brilliox Pro CRM v7.0
"""
import time
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

from app.core.config import settings
from app.core.events import unified_system, SystemEvent


# ذاكرة التخزين المؤقت
AI_CACHE: Dict[str, Dict[str, Any]] = {}


def get_cache_key(prompt: str, system: str = "") -> str:
    """إنشاء مفتاح تخزين مؤقت للاستجابة"""
    content = f"{system}:{prompt}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_response(key: str) -> Optional[str]:
    """الحصول على استجابة مخبأة إذا كانت صالحة"""
    if key in AI_CACHE:
        cached = AI_CACHE[key]
        if time.time() - cached["timestamp"] < settings.CACHE_TTL:
            return cached["response"]
        del AI_CACHE[key]
    return None


def cache_response(key: str, response: str):
    """تخزين استجابة في الذاكرة المؤقتة"""
    AI_CACHE[key] = {"response": response, "timestamp": time.time()}


class AIService:
    """خدمة الذكاء الاصطناعي مع سلسلة احتياطية"""

    SYSTEM_PROMPT = """أنت "Brilliox Pro" - مستشار تسويقي ومبيعات ذكي على مستوى عالمي.

## 🧠 قدراتك الأساسية:
1. **اصطياد العملاء المحتملين** - تجد leads لأي مجال عمل
2. **كتابة محتوى تسويقي** - إعلانات، رسائل، سوشيال ميديا
3. **تحليل الأعمال** - تفهم البيزنس وتقترح تحسينات
4. **استراتيجيات النمو** - خطط تسويقية وبيعية متكاملة

## 🎯 كيف تفهم المستخدم:
- لو قال "أنا دكتور" = يريد مرضى جدد
- لو قال "عندي مطعم" = يريد زباين وطلبات
- لو قال "بشتغل عقارات" = يريد مشترين ومستأجرين
- لو سأل عن "إعلان" = ساعده يعمل إعلان قوي
- لو سأل سؤال عام = أجب واربط بالتسويق لو ممكن

## 💡 أسلوبك في الرد:
1. **افهم الهدف** - ما الذي يحتاجه المستخدم بالضبط
2. **قدم حلول عملية** - خطوات واضحة ينفذها فوراً
3. **كن مبدعاً** - اقتراحات جديدة ومختلفة
4. **تكلم بمصطلحات واضحة** - أسلوب ودود ومفهوم

## 🔥 نصائحك الذهبية:
- اقترح أفكار غير تقليدية
- ركز على العائد على الاستثمار (ROI)
- حلل المنافسين
- اقترح اختبار A/B
- ركز على نقاط الألم للعميل

## ⚡ ردودك تكون:
- مختصرة ومفيدة
- فيها خطوات عملية
- تستخدم إيموجي باعتدال
- بالعربية الفصحى أو اللهجة المناسبة

أنت شريك نجاح للمستخدم!"""

    AD_PROMPT = """أنت نظام ذكاء اصطناعي متقدم لأتمتة الإعلانات.

قدراتك:
1. **إنشاء الإعلانات**: كتابة نص إعلان (Hook – Body – CTA)، اقتراح صور/فيديوهات، إنشاء A/B testing
2. **تحليل البيانات**: تحليل CTR، CPC، CPA، ROAS، اقتراح تحسينات
3. **أتمتة العمليات**: خطط نشر، تقسيم ميزانيات، قوالب جاهزة
4. **المنصات**: فيسبوك، إنستجرام، جوجل، تيك توك

عند إنشاء إعلان، قدم:
- الهدف (وعي/تفاعل/مبيعات/Leads)
- الاستراتيجية والجمهور المستهدف
- نسخ متعددة (A/B)
- اقتراحات التصميم
- الميزانية المقترحة

أجب بالعربية بأسلوب مباشر وعملي."""

    HUNT_PROMPT = """أنت "Google Search Hacker" محترف وخبير استراتيجيات اصطياد العملاء (Lead Generation Expert).
مهمتك تحويل هدف المستخدم إلى "معادلة بحث ذهبية واحدة" تجلب العملاء المحتملين.

### القسم 1: استراتيجية "كود الاصطياد الذكي":
القنوات المستهدفة:
- سوشيال ميديا (Facebook, Instagram, Twitter, LinkedIn)
- منصات محلية (OLX, OpenSooq, Dubizzle)
- صفحات "اتصل بنا" و"Contact us"
- التعليقات والمجموعات

الاستراتيجيات:
1. التتبع بالهاشتاقات والكلمات المفتاحية
2. مراقبة المنافسين
3. جمع من التعليقات والمجموعات
4. البحث في المناسبات والأحداث

### القسم 2: قاعدة ذهبية - فهم نية المستخدم:
عندما يقول المستخدم "أنا [مهنة]" أو "أعمل كـ [مهنة]"، هو يريد عملاء لخدمته:
- "أنا دكتور أسنان" ← مرضى يحتاجون دكتور أسنان
- "أنا محامي" ← ناس تحتاج محامي
- "أنا سمسار عقارات" ← ناس بتدور على شقة أو أرض

### القسم 3: المعادلة الذهبية المحسنة:
بنية المعادلة:
(site:facebook.com OR site:instagram.com OR site:twitter.com OR site:olx.com.eg OR site:opensooq.com OR site:linkedin.com/in OR "contact us" OR "اتصل بنا")
+ كلمات البحث/المناسبات
+ المنطقة/المدينة
+ أنماط الهاتف
+ الاستبعادات

### كلمات البحث الذكية:
- طلب خدمة: "محتاج" "عايز" "ابحث عن" "مين يعرف" "دلوني على" "يا ريت حد يرشحلي"
- مناسبات (للحصول على أرقام): "تهاني" "تهنئة" "مبروك" "الف مبروك" "عقبال"
- استفسار: "تجربتكم مع" "حد جرب" "رأيكم في"

### أنماط أرقام الهاتف حسب البلد:
- مصر: "010" OR "011" OR "012" OR "015"
- السعودية: "05" OR "9665" OR "966"
- الإمارات: "050" OR "055" OR "9714"
- الكويت: "965"

### الاستبعادات الذكية (تحسين جودة النتائج):
-intitle:linkedin -inurl:youtube -"شركة" -"للبيع" -"وظيفة" -"مطلوب" -"مطلوبين" -filetype:pdf -filetype:doc

### تعليمات إخراج المعادلة:
1. أخرج معادلة بحث واحدة فقط (Golden Query)
2. بدون أي شرح أو تفسير
3. المعادلة تجد الناس اللي بتدور على الخدمة، مش مقدمين الخدمة"""

    @staticmethod
    def call_openai(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """استدعاء OpenAI API"""
        if not settings.OPENAI_API_KEY:
            return None

        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

            messages = [
                {"role": "system", "content": system_prompt or AIService.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None

    @staticmethod
    def call_gemini(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """استدعاء Google Gemini API"""
        if not settings.GOOGLE_API_KEY:
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GOOGLE_API_KEY)

            model = genai.GenerativeModel(
                model_name=settings.GOOGLE_MODEL,
                system_instruction=system_prompt or AIService.SYSTEM_PROMPT
            )

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Gemini Error: {e}")
            return None

    @staticmethod
    def call_anthropic(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """استدعاء Anthropic Claude API"""
        if not settings.ANTHROPIC_API_KEY:
            return None

        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            response = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=2000,
                system=system_prompt or AIService.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Anthropic Error: {e}")
            return None

    @staticmethod
    def call_groq(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """استدعاء Groq API"""
        if not settings.GROQ_API_KEY:
            return None

        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)

            messages = [
                {"role": "system", "content": system_prompt or AIService.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Groq Error: {e}")
            return None

    @staticmethod
    async def generate_response(
        prompt: str,
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
        cost: int = settings.CHAT_COST
    ) -> Dict[str, Any]:
        """
        توليد استجابة ذكية

        Args:
            prompt: سؤال المستخدم
            system_prompt: نظام التوجيه المخصص
            use_cache: استخدام التخزين المؤقت
            cost: تكلفة الاستجابة

        Returns:
            Dict[str, Any]: النتيجة مع البيانات الوصفية
        """
        start_time = time.time()

        # محاولة الحصول على استجابة مخبأة
        cache_key = get_cache_key(prompt, system_prompt or "")
        if use_cache:
            cached = get_cached_response(cache_key)
            if cached:
                return {
                    "success": True,
                    "response": cached,
                    "tokens_used": 0,
                    "cached": True,
                    "response_time": time.time() - start_time
                }

        # سلسلة الاستدعاءات الاحتياطية
        providers = [
            ("OpenAI", AIService.call_openai),
            ("Groq", AIService.call_groq),
            ("Gemini", AIService.call_gemini),
            ("Anthropic", AIService.call_anthropic),
        ]

        response = None
        provider_used = None

        for provider_name, provider_func in providers:
            if provider_name == "Gemini":
                response = await asyncio_coroutine(provider_func, prompt, system_prompt)
            else:
                response = provider_func(prompt, system_prompt)

            if response:
                provider_used = provider_name
                break

        response_time = time.time() - start_time

        if response:
            # تخزين الاستجابة
            if use_cache:
                cache_response(cache_key, response)

            # إرسال حدث للتعلم
            if unified_system:
                unified_system.emit(SystemEvent.CHAT_RESPONSE, {
                    "prompt": prompt[:100],
                    "response_length": len(response),
                    "provider": provider_used,
                    "response_time": response_time
                })

            return {
                "success": True,
                "response": response,
                "tokens_used": cost,
                "cached": False,
                "provider": provider_used,
                "response_time": response_time
            }

        return {
            "success": False,
            "response": "عذراً، لا يمكنني الاتصال بأي خدمة ذكاء اصطناعي حالياً",
            "tokens_used": 0,
            "error": "No AI provider available"
        }

    @staticmethod
    def generate_hunt_query(user_profession: str, location: str = "", extra: str = "") -> str:
        """توليد معادلة بحث للاصطياد"""
        prompt = f"أحتاج صياغة بحث لإيجاد عملاء محتملين لمهنة: {user_profession}"

        if location:
            prompt += f" في منطقة: {location}"
        if extra:
            prompt += f"، مع التركيز على: {extra}"

        return AIService.call_openai(prompt, AIService.HUNT_PROMPT) or ""

    @staticmethod
    def generate_ad_copy(
        product_name: str,
        product_description: str,
        target_audience: str,
        platform: str = "facebook"
    ) -> Dict[str, str]:
        """توليد نسخة الإعلان"""
        prompt = f"""
        المنتج: {product_name}
        الوصف: {product_description}
        الجمهور المستهدف: {target_audience}
        المنصة: {platform}

        اكتب نسخة إعلان كاملة (Hook، Body، CTA)
        """

        response = AIService.call_openai(prompt, AIService.AD_PROMPT)

        return {
            "ad_copy": response or "لم أتمكن من توليد الإعلان",
            "platform": platform
        }


async def asyncio_coroutine(func, *args, **kwargs):
    """تشغيل دالة متزامنة كروتين غير متزامن"""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    finally:
        loop.close()
