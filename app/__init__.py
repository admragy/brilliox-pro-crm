"""
Brilliox Pro CRM - Application Package
v7.0.0 - Unified System
"""
__version__ = "7.0.0"
__author__ = "Brilliox Team"

from app.core.config import settings
from app.core.events import unified_system

__all__ = ["settings", "unified_system"]
