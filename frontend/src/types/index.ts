/**
 * Gamma AI — Shared TypeScript Types
 */

// ── WebSocket Message Types ─────────────────

export type WSMessageType =
  | "chat_message"
  | "chat_token"
  | "chat_done"
  | "voice_data"
  | "agent_event"
  | "notification"
  | "error"
  | "ack"
  | "heartbeat"
  | "interrupt";

export interface WSMessage {
  id: string;
  session_id: string;
  type: WSMessageType;
  payload: Record<string, unknown>;
  ts: string;
}

// ── Orb States ──────────────────────────────

export type OrbState = "idle" | "listening" | "thinking" | "speaking" | "error";

// ── Chat ────────────────────────────────────

export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  isStreaming: boolean;
  metadata?: Record<string, unknown>;
}

// ── Agent Events ────────────────────────────

export type AgentEventType =
  | "decision"
  | "memory_write"
  | "notification"
  | "tool_call"
  | "error";

export interface AgentEvent {
  id: string;
  agent_name: string;
  event_type: AgentEventType;
  title: string;
  detail: string;
  metadata: Record<string, unknown>;
  timestamp: string;
}

// ── Notifications ───────────────────────────

export type NotificationPriority = "info" | "warning" | "critical";

export interface Notification {
  id: string;
  title: string;
  body: string;
  priority: NotificationPriority;
  action_url?: string;
  read: boolean;
  timestamp: string;
}

// ── Memory ──────────────────────────────────

export type MemoryType = "general" | "preference" | "fact" | "event";

export interface MemoryRecord {
  id: string;
  content: string;
  memory_type: MemoryType;
  importance: number;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ── User ────────────────────────────────────

export interface UserProfile {
  id: string;
  session_id: string;
  display_name: string;
  preferences: Record<string, unknown>;
  created_at?: string;
}

// ── Connection ──────────────────────────────

export type ConnectionState =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected";

// ── Session ─────────────────────────────────

export interface SessionResponse {
  session_id: string;
  token: string;
}

// ── Health ──────────────────────────────────

export interface HealthResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}
