"""
CRM Module - Customer Relationship Management
Brilliox Pro CRM v7.0
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from app.core.config import settings
from app.services.lead_service import LeadService
from app.services.user_service import UserService


class CRMStats:
    """إحصائيات CRM"""

    @staticmethod
    def get_overall_stats() -> Dict[str, Any]:
        """الحصول على الإحصائيات العامة"""
        all_leads = LeadService.get_all_leads()
        all_users = UserService.get_all_users()

        # حساب الإحصائيات
        status_counts = {}
        source_counts = {}

        for lead in all_leads:
            status = lead.get('status', 'unknown')
            source = lead.get('source', 'unknown')

            status_counts[status] = status_counts.get(status, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1

        # حساب معدل التحويل
        total = len(all_leads)
        closed = status_counts.get('closed', 0)
        conversion_rate = (closed / total * 100) if total > 0 else 0

        return {
            "total_leads": total,
            "total_users": len(all_users),
            "status_distribution": status_counts,
            "source_distribution": source_counts,
            "conversion_rate": round(conversion_rate, 2),
            "generated_at": datetime.now().isoformat()
        }

    @staticmethod
    def get_user_performance(user_id: str) -> Dict[str, Any]:
        """الحصول على أداء مستخدم"""
        leads = LeadService.get_user_leads(user_id)
        user = UserService.get_or_create(user_id)

        status_counts = {}
        total_value = 0

        for lead in leads:
            status = lead.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "user_id": user_id,
            "wallet_balance": user.get("wallet_balance", 0),
            "total_leads": len(leads),
            "leads_by_status": status_counts,
            "is_admin": user.get("is_admin", False)
        }


class CRMAnalytics:
    """تحليلات CRM"""

    @staticmethod
    def analyze_lead_sources() -> Dict[str, Any]:
        """تحليل مصادر العملاء"""
        all_leads = LeadService.get_all_leads()

        source_analysis = {}
        for lead in all_leads:
            source = lead.get('source', 'unknown')
            if source not in source_analysis:
                source_analysis[source] = {
                    "count": 0,
                    "converted": 0,
                    "total_score": 0
                }

            source_analysis[source]["count"] += 1

            if lead.get('status') == 'closed':
                source_analysis[source]["converted"] += 1

            source_analysis[source]["total_score"] += lead.get('score', 0)

        # حساب التحويل لكل مصدر
        for source, data in source_analysis.items():
            if data["count"] > 0:
                data["conversion_rate"] = round(
                    data["converted"] / data["count"] * 100, 2
                )
                data["avg_score"] = round(
                    data["total_score"] / data["count"], 2
                )

        return {
            "sources": source_analysis,
            "best_source": max(
                source_analysis.items(),
                key=lambda x: x[1].get("conversion_rate", 0)
            )[0] if source_analysis else None,
            "analyzed_at": datetime.now().isoformat()
        }

    @staticmethod
    def get_funnel_analysis() -> Dict[str, Any]:
        """تحليل قمع المبيعات"""
        all_leads = LeadService.get_all_leads()

        funnel = {
            "new": 0,
            "bait_sent": 0,
            "replied": 0,
            "interested": 0,
            "negotiating": 0,
            "hot": 0,
            "closed": 0,
            "lost": 0
        }

        for lead in all_leads:
            status = lead.get('status', 'new')
            if status in funnel:
                funnel[status] += 1

        # حساب النسب المئوية
        total = sum(funnel.values())
        funnel_percentages = {}
        for status, count in funnel.items():
            funnel_percentages[status] = {
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0
            }

        return {
            "funnel": funnel_percentages,
            "total_leads": total,
            "analyzed_at": datetime.now().isoformat()
        }


class CRMExport:
    """تصدير البيانات"""

    @staticmethod
    def export_leads_csv(user_id: str = None) -> str:
        """تصدير العملاء كـ CSV"""
        if user_id:
            leads = LeadService.get_user_leads(user_id)
        else:
            leads = LeadService.get_all_leads()

        lines = ["id,name,phone,email,status,source,score,created_at"]

        for lead in leads:
            line = f"{lead.get('id','')},{lead.get('name','')},{lead.get('phone','')},"
            line += f"{lead.get('email','')},{lead.get('status','')},"
            line += f"{lead.get('source','')},{lead.get('score',0)},{lead.get('created_at','')}"
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def export_stats_json() -> str:
        """تصدير الإحصائيات كـ JSON"""
        import json
        stats = {
            "overall": CRMStats.get_overall_stats(),
            "funnel": CRMAnalytics.get_funnel_analysis(),
            "sources": CRMAnalytics.analyze_lead_sources()
        }
        return json.dumps(stats, ensure_ascii=False, indent=2)


# دوال مساعدة للوصول السريع

def get_crm_stats() -> Dict[str, Any]:
    """الحصول على إحصائيات CRM"""
    return CRMStats.get_overall_stats()


def get_user_crm_stats(user_id: str) -> Dict[str, Any]:
    """الحصول على إحصائيات مستخدم"""
    return CRMStats.get_user_performance(user_id)


def analyze_sources() -> Dict[str, Any]:
    """تحليل المصادر"""
    return CRMAnalytics.analyze_lead_sources()


def get_funnel() -> Dict[str, Any]:
    """الحصول على قمع المبيعات"""
    return CRMAnalytics.get_funnel_analysis()
