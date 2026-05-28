"""Gamma AI — Pydantic v2 Schemas for all API I/O."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────

class WSMessageType(str, Enum):
    """WebSocket message types."""
    CHAT_MESSAGE = "chat_message"
    CHAT_TOKEN = "chat_token"
    CHAT_DONE = "chat_done"
    VOICE_DATA = "voice_data"
    AGENT_EVENT = "agent_event"
    NOTIFICATION = "notification"
    ERROR = "error"
    ACK = "ack"
    HEARTBEAT = "heartbeat"
    INTERRUPT = "interrupt"


class OrbState(str, Enum):
    """AI Orb visual states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"


class AgentEventType(str, Enum):
    """Agent event types for timeline."""
    DECISION = "decision"
    MEMORY_WRITE = "memory_write"
    NOTIFICATION = "notification"
    TOOL_CALL = "tool_call"
    ERROR = "error"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MemoryType(str, Enum):
    """Memory record types."""
    GENERAL = "general"
    PREFERENCE = "preference"
    FACT = "fact"
    EVENT = "event"


# ── WebSocket Envelope ────────────────────────

class WSMessage(BaseModel):
    """Universal WebSocket message envelope."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    type: WSMessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    ts: datetime = Field(default_factory=lambda: datetime.now())


# ── Chat ──────────────────────────────────────

class ChatMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A single chat message."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: ChatMessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    is_streaming: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """REST API chat request."""
    message: str
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """REST API chat response."""
    message: ChatMessage
    session_id: str
    conversation_id: str


# ── Agent Events ──────────────────────────────

class AgentEventSchema(BaseModel):
    """Agent event for timeline display."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_name: str
    event_type: AgentEventType
    title: str
    detail: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


# ── Notifications ─────────────────────────────

class Notification(BaseModel):
    """Proactive notification."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.INFO
    action_url: Optional[str] = None
    read: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


# ── Memory ────────────────────────────────────

class MemoryRecord(BaseModel):
    """Memory record schema."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    memory_type: MemoryType = MemoryType.GENERAL
    importance: float = 0.5
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class MemoryCreateRequest(BaseModel):
    """Request to create a memory record."""
    content: str
    memory_type: MemoryType = MemoryType.GENERAL
    importance: float = 0.5


class MemorySearchRequest(BaseModel):
    """Request to search memories."""
    query: str
    top_k: int = 5
    memory_type: Optional[MemoryType] = None


# ── User Profile ──────────────────────────────

class UserProfile(BaseModel):
    """User profile with preferences."""
    id: str
    session_id: str
    display_name: str = "User"
    preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


# ── Health Check ──────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict[str, str] = Field(default_factory=dict)


# ── Session ───────────────────────────────────

class SessionResponse(BaseModel):
    """Auto-issued session response."""
    session_id: str
    token: str
