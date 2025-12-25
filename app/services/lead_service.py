"""
Lead Service - Lead Management and Scoring
Brilliox Pro CRM v7.0
"""
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.config import settings
from app.core.database import DatabaseOperations
from app.core.events import unified_system, SystemEvent, LeadStage


class LeadService:
    """خدمة إدارة العملاء المحتملين"""

    @staticmethod
    def add_lead(user_id: str, lead_data: Dict[str, Any]) -> str:
        """
        إضافة عميل محتمل جديد

        Args:
            user_id: معرف المستخدم
            lead_data: بيانات العميل

        Returns:
            str: معرف العميل الجديد
        """
        # تنظيف البيانات
        clean_data = {
            'name': str(lead_data.get('name', '')).strip(),
            'phone': str(lead_data.get('phone', '')).strip(),
            'email': str(lead_data.get('email', '')).strip() if lead_data.get('email') else None,
            'status': lead_data.get('status', 'new'),
            'notes': str(lead_data.get('notes', '')).strip() if lead_data.get('notes') else None,
            'source': lead_data.get('source', 'manual'),
            'campaign': lead_data.get('campaign', None),
            'score': 0,
            'user_id': user_id
        }

        # إضافة العميل
        lead_id = DatabaseOperations.add_lead(user_id, clean_data)

        # إرسال حدث
        if unified_system:
            unified_system.emit(SystemEvent.LEAD_ADDED, {
                'lead_id': lead_id,
                'user_id': user_id,
                'source': clean_data['source'],
                'name': clean_data['name']
            })

        return lead_id

    @staticmethod
    def get_user_leads(user_id: str) -> List[Dict[str, Any]]:
        """الحصول على عملاء المستخدم"""
        return DatabaseOperations.get_leads(user_id)

    @staticmethod
    def get_all_leads() -> List[Dict[str, Any]]:
        """الحصول على جميع العملاء"""
        return DatabaseOperations.get_all_leads()

    @staticmethod
    def update_lead(lead_id: str, updates: Dict[str, Any]) -> bool:
        """تحديث بيانات عميل"""
        updates['updated_at'] = datetime.now().isoformat()

        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').update(updates).eq('id', lead_id).execute()
                return bool(result.data)
            except Exception as e:
                print(f"Error updating lead: {e}")

        return False

    @staticmethod
    def update_lead_status(lead_id: str, new_status: str) -> bool:
        """تحديث حالة العميل"""
        old_status = None

        # الحصول على الحالة القديمة
        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').select('status').eq('id', lead_id).execute()
                if result.data:
                    old_status = result.data[0].get('status')
            except Exception as e:
                print(f"Error getting lead status: {e}")

        # التحديث
        success = LeadService.update_lead(lead_id, {'status': new_status})

        if success and old_status != new_status:
            if unified_system:
                unified_system.emit(SystemEvent.LEAD_STAGE_CHANGED, {
                    'lead_id': lead_id,
                    'old_status': old_status,
                    'new_status': new_status
                })

        return success

    @staticmethod
    def delete_lead(lead_id: str) -> bool:
        """حذف عميل"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').delete().eq('id', lead_id).execute()
                return bool(result.data)
            except Exception as e:
                print(f"Error deleting lead: {e}")

        return False

    @staticmethod
    def share_lead(user_id: str, share_with: str, lead_id: str,
                   status: str = "new", notes: str = "") -> bool:
        """مشاركة عميل مع مستخدم آخر"""
        # التحقق من صلاحية المستخدم
        lead = LeadService.get_lead_by_id(lead_id)
        if not lead or lead.get('user_id') != user_id:
            return False

        # إنشاء مشاركة
        share_data = {
            'lead_id': lead_id,
            'shared_by': user_id,
            'shared_with': share_with,
            'status': status,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }

        client = get_supabase_client()
        if client:
            try:
                result = client.table('lead_shares').insert(share_data).execute()
                return bool(result.data)
            except Exception as e:
                print(f"Error sharing lead: {e}")

        return False

    @staticmethod
    def get_lead_by_id(lead_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على عميل بالمعرف"""
        client = get_supabase_client()
        if client:
            try:
                result = client.table('leads').select('*').eq('id', lead_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Error getting lead: {e}")

        return None

    @staticmethod
    def get_lead_stats(user_id: str) -> Dict[str, Any]:
        """الحصول على إحصائيات العملاء"""
        leads = LeadService.get_user_leads(user_id)

        stats = {
            'total': len(leads),
            'by_status': {},
            'conversion_rate': 0.0
        }

        # حساب الإحصائيات حسب الحالة
        for lead in leads:
            status = lead.get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

        # حساب معدل التحويل
        closed = stats['by_status'].get('closed', 0)
        if stats['total'] > 0:
            stats['conversion_rate'] = round((closed / stats['total']) * 100, 2)

        return stats

    @staticmethod
    def import_leads(user_id: str, leads_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """استيراد مجموعة من العملاء"""
        imported = 0
        duplicates = 0
        errors = 0

        for lead in leads_data:
            try:
                if not lead.get('name') and not lead.get('phone'):
                    errors += 1
                    continue

                LeadService.add_lead(user_id, {
                    'name': lead.get('name', ''),
                    'phone': lead.get('phone', ''),
                    'email': lead.get('email', ''),
                    'status': 'new',
                    'source': 'import'
                })
                imported += 1

            except Exception:
                errors += 1

        return {
            'imported': imported,
            'duplicates': duplicates,
            'errors': errors
        }


class LeadScorer:
    """تقييم العملاء باستخدام الذكاء الاصطناعي"""

    @staticmethod
    def calculate_score(lead: Dict[str, Any]) -> Dict[str, Any]:
        """حساب درجة العميل"""
        score = 0
        factors = []

        # التحقق من اكتمال البيانات
        if lead.get('name'):
            score += 10
            factors.append({"factor": "اسم متوفر", "points": 10})

        if lead.get('phone'):
            score += 10
            factors.append({"factor": "رقم هاتف متوفر", "points": 10})

        if lead.get('email'):
            score += 5
            factors.append({"factor": "بريد إلكتروني متوفر", "points": 5})

        # تحليل الحالة
        status_scores = {
            'new': 10,
            'bait_sent': 25,
            'replied': 40,
            'interested': 55,
            'negotiating': 70,
            'hot': 85,
            'closed': 100
        }
        score = max(score, status_scores.get(lead.get('status', 'new'), 0))

        # تحليل الملاحظات
        notes = lead.get('notes', '')
        positive_words = ['مهتم', 'سعيد', 'رائع', 'ممتاز']
        negative_words = ['لا', 'مش', 'فاهم', 'معقد']

        for word in positive_words:
            if word in notes:
                score += 5
                factors.append({"factor": f"كلمة إيجابية: {word}", "points": 5})

        for word in negative_words:
            if word in notes:
                score -= 5
                factors.append({"factor": f"كلمة سلبية: {word}", "points": -5})

        return {
            'score': min(100, max(0, score)),
            'grade': LeadScorer._get_grade(score),
            'factors': factors
        }

    @staticmethod
    def _get_grade(score: int) -> str:
        """الحصول على التقدير"""
        if score >= 90:
            return "ممتاز"
        elif score >= 70:
            return "جيد جداً"
        elif score >= 50:
            return "جيد"
        elif score >= 30:
            return "متوسط"
        else:
            return "ضعيف"

    @staticmethod
    def score_leads_batch(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """تقييم مجموعة من العملاء"""
        scored = []
        for lead in leads:
            scoring = LeadScorer.calculate_score(lead)
            lead['score'] = scoring['score']
            lead['grade'] = scoring['grade']
            lead['score_factors'] = scoring['factors']
            scored.append(lead)
        return scored

    @staticmethod
    def get_insights(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """الحصول على رؤى لتحسين المبيعات"""
        scored_leads = LeadScorer.score_leads_batch(leads)

        hot_leads = [l for l in scored_leads if l.get('score', 0) >= 70]
        cold_leads = [l for l in scored_leads if l.get('score', 0) < 30]

        return {
            'total_leads': len(scored_leads),
            'hot_leads_count': len(hot_leads),
            'cold_leads_count': len(cold_leads),
            'average_score': sum(l.get('score', 0) for l in scored_leads) / len(scored_leads) if scored_leads else 0,
            'recommendations': LeadScorer._generate_recommendations(hot_leads, cold_leads)
        }

    @staticmethod
    def _generate_recommendations(hot_leads: List, cold_leads: List) -> List[str]:
        """توليد توصيات"""
        recommendations = []

        if len(hot_leads) > 0:
            recommendations.append(f"لديك {len(hot_leads)} عميل ساخن يجب التواصل معهم فوراً")

        if len(cold_leads) > 0:
            recommendations.append(f"فكر في إعادة تنشيط {len(cold_leads)} عميل بارد")

        if not hot_leads and not cold_leads:
            recommendations.append("أضف المزيد من العملاء للحصول على رؤى")

        return recommendations


def get_supabase_client():
    """استيراد عميل Supabase"""
    from app.core.database import get_supabase_client
    return get_supabase_client()
