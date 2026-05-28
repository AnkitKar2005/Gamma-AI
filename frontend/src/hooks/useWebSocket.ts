"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ConnectionState, WSMessage, WSMessageType } from "@/types";
import { createHeartbeat, createWSMessage } from "@/services/ws";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8080/ws";

// Reconnect backoff: 1s → 2s → 4s → 8s → 16s max
const BACKOFF_BASE = 1000;
const BACKOFF_MAX = 16000;

interface UseWebSocketOptions {
  sessionId: string;
  autoConnect?: boolean;
  onMessage?: (type: WSMessageType, payload: Record<string, unknown>, message: WSMessage) => void;
}

interface UseWebSocketReturn {
  connectionState: ConnectionState;
  sendMessage: (type: WSMessageType, payload: Record<string, unknown>) => void;
  connect: () => void;
  disconnect: () => void;
  lastMessage: WSMessage | null;
}

export function useWebSocket({
  sessionId,
  autoConnect = true,
  onMessage,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempt = useRef(0);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const messageQueue = useRef<WSMessage[]>([]);
  const onMessageRef = useRef(onMessage);

  // Keep onMessage ref up to date without re-triggering effects
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const clearTimers = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    if (heartbeatTimer.current) {
      clearInterval(heartbeatTimer.current);
      heartbeatTimer.current = null;
    }
  }, []);

  const flushQueue = useCallback((ws: WebSocket) => {
    while (messageQueue.current.length > 0) {
      const msg = messageQueue.current.shift()!;
      try {
        ws.send(JSON.stringify(msg));
      } catch {
        messageQueue.current.unshift(msg);
        break;
      }
    }
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionState(reconnectAttempt.current > 0 ? "reconnecting" : "connecting");

    const url = `${WS_BASE}/${sessionId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionState("connected");
      reconnectAttempt.current = 0;
      flushQueue(ws);

      // Start heartbeat every 25s (server expects within 30s)
      heartbeatTimer.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(createHeartbeat(sessionId)));
        }
      }, 25000);
    };

    ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        setLastMessage(message);

        // Don't surface heartbeats/acks to app level
        if (message.type !== "heartbeat" && message.type !== "ack") {
          onMessageRef.current?.(message.type as WSMessageType, message.payload, message);
        }
      } catch {
        console.warn("[WS] Failed to parse message:", event.data);
      }
    };

    ws.onerror = (error) => {
      // Don't use console.error to avoid triggering disruptive dev overlays
      // WebSocket error events are often opaque/empty for security reasons
      console.warn("[WS] Connection error. Is the backend running at", WS_BASE, "?", error);
    };

    ws.onclose = (event) => {
      clearTimers();
      wsRef.current = null;

      // Don't reconnect if intentionally closed (code 1000 or 4000)
      if (event.code === 1000 || event.code === 4000) {
        setConnectionState("disconnected");
        return;
      }

      setConnectionState("reconnecting");

      // Exponential backoff reconnect
      const delay = Math.min(BACKOFF_BASE * Math.pow(2, reconnectAttempt.current), BACKOFF_MAX);
      reconnectAttempt.current += 1;

      reconnectTimer.current = setTimeout(() => {
        connect();
      }, delay);
    };
  }, [sessionId, clearTimers, flushQueue]);

  const disconnect = useCallback(() => {
    clearTimers();
    if (wsRef.current) {
      wsRef.current.close(1000, "Client disconnect");
      wsRef.current = null;
    }
    setConnectionState("disconnected");
  }, [clearTimers]);

  const sendMessage = useCallback(
    (type: WSMessageType, payload: Record<string, unknown>) => {
      const msg = createWSMessage(type, payload, sessionId);

      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(msg));
      } else {
        // Queue for when connection is restored
        messageQueue.current.push(msg);
      }
    },
    [sessionId]
  );

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect && sessionId) {
      connect();
    }
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, autoConnect]);

  return {
    connectionState,
    sendMessage,
    connect,
    disconnect,
    lastMessage,
  };
}
