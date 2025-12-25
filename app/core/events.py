"""
نظام الأحداث الموحد - Event-Driven Architecture
Brilliox Pro CRM v7.0
"""
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import asyncio
import json
import os
from pathlib import Path


class SystemEvent(Enum):
    """أحداث النظام الرئيسية"""
    # أحداث العملاء المحتملين
    LEAD_ADDED = "lead_added"
    LEAD_UPDATED = "lead_updated"
    LEAD_DELETED = "lead_deleted"
    LEAD_STAGE_CHANGED = "lead_stage_changed"
    LEAD_DISTRIBUTED = "lead_distributed"
    LEAD_SCORED = "lead_scored"

    # أحداث الحملات
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_STOPPED = "campaign_stopped"
    CAMPAIGN_COMPLETED = "campaign_completed"

    # أحداث الرسائل
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"

    # أحداث المحادثة
    CHAT_MESSAGE = "chat_message"
    CHAT_RESPONSE = "chat_response"

    # أحداث التعلم
    AI_LEARNING = "ai_learning"
    AI_STYLE_CHANGE = "ai_style_change"
    PATTERN_LEARNED = "pattern_learned"

    # أحداث الإدارة
    ADMIN_MODIFICATION = "admin_modification"
    ADMIN_COMMAND = "admin_command"
    ADMIN_TEACH = "admin_teach"

    # أحداث التحويل
    CONVERSION_SUCCESS = "conversion_success"
    CONVERSION_FAILED = "conversion_failed"

    # أحداث النظام
    SYSTEM_ERROR = "system_error"
    SYSTEM_READY = "system_ready"
    SYSTEM_SHUTDOWN = "system_shutdown"


class UserType(Enum):
    """أنواع المستخدمين في النظام"""
    ADMIN = "admin"
    USER = "user"
    CLIENT = "client"


class LeadStage(Enum):
    """مراحل قمع المبيعات"""
    NEW = "new"
    BAIT_SENT = "bait_sent"
    REPLIED = "replied"
    INTERESTED = "interested"
    NEGOTIATING = "negotiating"
    HOT = "hot"
    CLOSED = "closed"
    LOST = "lost"


class UnifiedSystem:
    """
    النظام الموحد - مركز الأحداث المعماري
    يربط جميع مكونات النظام معاً
    """

    _instance: Optional['UnifiedSystem'] = None
    _initialized: bool = False

    def __new__(cls) -> 'UnifiedSystem':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not UnifiedSystem._initialized:
            self._listeners: Dict[SystemEvent, List[Callable]] = {}
            self._state: Dict[str, Any] = {}
            self._rules: List[Dict] = []
            self._learned_patterns: List[Dict] = []
            self._active_campaigns: Dict[str, Dict] = {}
            self._event_history: List[Dict] = []
            self._data_file = Path("data/system_data.json")
            self._load_data()
            UnifiedSystem._initialized = True

    def _load_data(self):
        """تحميل البيانات المحفوظة"""
        try:
            if self._data_file.exists():
                with open(self._data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._state = data.get('state', {})
                    self._rules = data.get('rules', [])
                    self._learned_patterns = data.get('patterns', [])
        except Exception as e:
            print(f"Error loading system data: {e}")

    def _save_data(self):
        """حفظ البيانات"""
        try:
            # إنشاء نسخة من القواعد بدون الدوال (لأنها لا يمكن تسلسلها)
            serializable_rules = []
            for rule in self._rules:
                serializable_rule = {
                    'id': rule.get('id'),
                    'name': rule.get('name'),
                    'action': rule.get('action')
                }
                serializable_rules.append(serializable_rule)

            data = {
                'state': self._state,
                'rules': serializable_rules,
                'patterns': self._learned_patterns
            }
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving system data: {e}")

    def initialize(self):
        """تهيئة النظام"""
        self._state = {
            "initialized_at": datetime.now().isoformat(),
            "version": "7.0.0",
            "total_events": 0,
            "active_users": 0,
            "total_leads": 0,
            "conversion_rate": 0.0,
            "system_status": "ready"
        }
        self._rules = self._load_default_rules()
        self._listeners = {event: [] for event in SystemEvent}
        self._save_data()
        print("System initialized successfully")

    def _load_default_rules(self) -> List[Dict]:
        """تحميل القواعد الافتراضية"""
        return [
            {
                "id": "auto_score_new_leads",
                "name": "تقييم العملاء الجدد تلقائياً",
                "condition": lambda data: data.get("event") == SystemEvent.LEAD_ADDED,
                "action": "score_lead"
            },
            {
                "id": "notify_admin_on_hot_lead",
                "name": "إشعار الأدمن عند عميل ساخن",
                "condition": lambda data: data.get("stage") == "hot",
                "action": "notify_admin"
            }
        ]

    def on(self, event: SystemEvent) -> Callable:
        """ديكوريتور للتسجيل في الأحداث"""
        def decorator(func: Callable):
            if event not in self._listeners:
                self._listeners[event] = []
            self._listeners[event].append(func)
            return func
        return decorator

    def emit(self, event: SystemEvent, data: Dict[str, Any]) -> None:
        """إرسال حدث لجميع المستمعين"""
        if event not in self._listeners:
            return

        self._state["total_events"] += 1
        event_record = {
            "event": event.value,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self._event_history.append(event_record)

        # الاحتفاظ بـ 1000 حدث فقط في التاريخ
        if len(self._event_history) > 1000:
            self._event_history = self._event_history[-1000:]

        # تنفيذ المستمعين بشكل متزامن
        for callback in self._listeners[event]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(event, data))
                else:
                    callback(event, data)
            except Exception as e:
                print(f"Error in event listener: {e}")

        # التحقق من القواعد
        self._check_rules(event, data)
        self._save_data()

    def _check_rules(self, event: SystemEvent, data: Dict[str, Any]) -> None:
        """التحقق من القواعد وتنفيذ الإجراءات"""
        for rule in self._rules:
            try:
                if rule["condition"]({"event": event, **data}):
                    action = rule.get("action")
                    if action == "score_lead":
                        self._auto_score_lead(data)
                    elif action == "notify_admin":
                        self._notify_admin(data)
            except Exception as e:
                print(f"Error checking rule {rule.get('id')}: {e}")

    def _auto_score_lead(self, data: Dict[str, Any]) -> None:
        """تقييم تلقائي للعميل الجديد"""
        lead_id = data.get("lead_id")
        if lead_id:
            print(f"Auto-scoring lead: {lead_id}")

    def _notify_admin(self, data: Dict[str, Any]) -> None:
        """إشعار الأدمن"""
        lead_id = data.get("lead_id")
        print(f"Notifying admin about hot lead: {lead_id}")

    def add_rule(self, rule: Dict) -> None:
        """إضافة قاعدة جديدة"""
        self._rules.append(rule)
        self._save_data()

    def remove_rule(self, rule_id: str) -> None:
        """حذف قاعدة"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]
        self._save_data()

    def learn_pattern(self, pattern: Dict) -> None:
        """تعلم نمط جديد"""
        pattern["learned_at"] = datetime.now().isoformat()
        self._learned_patterns.append(pattern)
        # الاحتفاظ بـ 500 نمط فقط
        if len(self._learned_patterns) > 500:
            self._learned_patterns = self._learned_patterns[-500:]
        self._save_data()

    def get_patterns(self) -> List[Dict]:
        """الحصول على الأنماط المتعلمة"""
        return self._learned_patterns

    def get_state(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        return self._state

    def update_state(self, key: str, value: Any) -> None:
        """تحديث حالة النظام"""
        self._state[key] = value
        self._save_data()

    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        return {
            **self._state,
            "active_rules": len(self._rules),
            "learned_patterns": len(self._learned_patterns),
            "event_history_count": len(self._event_history)
        }


# إنشاء نسخة واحدة من النظام
unified_system = UnifiedSystem()
