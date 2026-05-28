"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Brain, Zap, Bell, Wrench, AlertTriangle } from "lucide-react";
import { useTimelineStore } from "@/store/timelineStore";
import type { AgentEventType } from "@/types";

const eventConfig: Record<AgentEventType, { icon: typeof Brain; color: string }> = {
  decision: { icon: Brain, color: "#22c55e" },
  memory_write: { icon: Zap, color: "#8b5cf6" },
  notification: { icon: Bell, color: "#f59e0b" },
  tool_call: { icon: Wrench, color: "#3b82f6" },
  error: { icon: AlertTriangle, color: "#ef4444" },
};

export default function AITimeline() {
  const events = useTimelineStore((s) => s.events);

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <h2
          style={{
            fontSize: 14,
            fontWeight: 600,
            color: "var(--text-secondary)",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
          }}
        >
          AI Timeline
        </h2>
        <span className="badge badge-purple">Live</span>
      </div>

      {events.length === 0 ? (
        <p style={{ fontSize: 13, color: "var(--text-muted)", textAlign: "center", padding: 24 }}>
          No agent events yet. Start a conversation to see activity.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <AnimatePresence initial={false}>
            {events.map((event, i) => {
              const config = eventConfig[event.event_type] || eventConfig.tool_call;
              const Icon = config.icon;

              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: 20, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: "auto" }}
                  exit={{ opacity: 0, x: -20, height: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05 }}
                  className="card"
                  style={{ padding: 14, cursor: "pointer" }}
                >
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: "var(--radius-md)",
                        background: `${config.color}15`,
                        border: `1px solid ${config.color}30`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                      }}
                    >
                      <Icon size={14} color={config.color} />
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          marginBottom: 4,
                        }}
                      >
                        <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                          {event.title}
                        </span>
                        <span style={{ fontSize: 11, color: "var(--text-muted)", flexShrink: 0 }}>
                          {new Date(event.timestamp).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                      {event.detail && (
                        <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.4 }}>
                          {event.detail}
                        </p>
                      )}
                    </div>

                    <ChevronRight size={14} color="var(--text-muted)" style={{ marginTop: 3, flexShrink: 0 }} />
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
