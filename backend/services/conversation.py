"""
会话管理服务 — 管理多 org_id 会话上下文
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime


class ConversationContext:
    def __init__(self):
        self.conversation_id: str = ""
        self.org_id: str = ""
        self.messages: List[Dict] = []
        self.created_at: datetime = datetime.now()
        self.last_updated: datetime = datetime.now()


class ConversationService:
    """会话管理服务"""
    _store: Dict[str, ConversationContext] = {}

    @classmethod
    def create_conversation(cls, org_id: str) -> str:
        conv_id = f"conv_{uuid.uuid4().hex[:12]}"
        ctx = ConversationContext()
        ctx.conversation_id = conv_id
        ctx.org_id = org_id
        cls._store[conv_id] = ctx
        return conv_id

    @classmethod
    def get_conversation(cls, conversation_id: str) -> Optional[ConversationContext]:
        return cls._store.get(conversation_id)

    @classmethod
    def add_message(cls, conversation_id: str, role: str, content: str):
        ctx = cls._store.get(conversation_id)
        if ctx:
            ctx.messages.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
            ctx.last_updated = datetime.now()

    @classmethod
    def get_recent_sql(cls, conversation_id: str, limit: int = 3) -> List[str]:
        """获取最近生成的 SQL，用于上下文学习"""
        ctx = cls._store.get(conversation_id)
        if not ctx:
            return []
        sqls = [
            m["content"] for m in ctx.messages[-limit*2:]
            if m["role"] == "assistant" and "SELECT" in m.get("content", "").upper()
        ]
        return sqls[-limit:]
