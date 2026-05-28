/**
 * Gamma AI — WebSocket Message Types & Factories
 */

import type { WSMessage, WSMessageType } from "@/types";

// ── UUID Generator ──────────────────────────

export function generateId(): string {
  return crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

// ── Message Factory ─────────────────────────

export function createWSMessage(
  type: WSMessageType,
  payload: Record<string, unknown>,
  sessionId: string
): WSMessage {
  return {
    id: generateId(),
    session_id: sessionId,
    type,
    payload,
    ts: new Date().toISOString(),
  };
}

// ── Typed Message Factories ─────────────────

export function createChatMessage(content: string, sessionId: string): WSMessage {
  return createWSMessage("chat_message", { content }, sessionId);
}

export function createVoiceData(audioData: string, sessionId: string): WSMessage {
  return createWSMessage("voice_data", { audio: audioData }, sessionId);
}

export function createInterrupt(sessionId: string): WSMessage {
  return createWSMessage("interrupt", {}, sessionId);
}

export function createHeartbeat(sessionId: string): WSMessage {
  return createWSMessage("heartbeat", { client_time: Date.now() }, sessionId);
}

export function createAck(ackId: string, sessionId: string): WSMessage {
  return createWSMessage("ack", { ack_id: ackId }, sessionId);
}
