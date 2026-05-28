"use client";

import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { motion, AnimatePresence } from "framer-motion";
import { useViewStore } from "@/store/viewStore";
import AIOrb from "@/components/orb/AIOrb";
import ChatPanel from "@/components/chat/ChatPanel";
import ChatInput from "@/components/chat/ChatInput";
import AITimeline from "@/components/timeline/AITimeline";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useChatStore } from "@/store/chatStore";
import { Brain, Zap, Clock } from "lucide-react";

export default function Dashboard() {
  const { activeTab } = useViewStore();
  const { sendMessage } = useWebSocket({ sessionId: "dev-session" });
  const messages = useChatStore((s) => s.messages);

  const quickActions = [
    {
      icon: Brain,
      label: "What do you remember about me?",
      color: "#8b5cf6",
    },
    {
      icon: Zap,
      label: "Check Bitcoin price",
      color: "#f59e0b",
    },
    {
      icon: Clock,
      label: "What's the weather like?",
      color: "#3b82f6",
    },
  ];

  const handleQuickAction = (label: string) => {
    sendMessage("chat_message", { text: label });
  };

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <Header />

      {/* ── Main Content ──────────────────── */}
      <main className="dashboard-main">
        <AnimatePresence mode="wait">
          {activeTab === "home" && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                flex: 1,
                gap: 32,
                position: "relative",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  top: "30%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  width: 500,
                  height: 500,
                  background:
                    "radial-gradient(ellipse at center, rgba(139, 92, 246, 0.08) 0%, transparent 70%)",
                  pointerEvents: "none",
                }}
              />

              <AIOrb />

              <div style={{ textAlign: "center" }}>
                <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 8, lineHeight: 1.2 }}>
                  Hello, <span className="gradient-text">what can I help with?</span>
                </h1>
                <p style={{ fontSize: 15, color: "var(--text-muted)", maxWidth: 480 }}>
                  I&apos;m Gamma — your AI operating system. Ask me anything, and I&apos;ll use my agents to help.
                </p>
              </div>

              <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center", maxWidth: 600 }}>
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <motion.button
                      key={action.label}
                      whileHover={{ scale: 1.03, y: -2 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => handleQuickAction(action.label)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "10px 16px",
                        borderRadius: "var(--radius-full)",
                        background: "var(--bg-card)",
                        border: "1px solid var(--border-subtle)",
                        color: "var(--text-secondary)",
                        cursor: "pointer",
                        fontSize: 13,
                        transition: "all var(--transition-fast)",
                      }}
                    >
                      <Icon size={16} color={action.color} />
                      {action.label}
                    </motion.button>
                  );
                })}
              </div>

              <div style={{ width: "100%", maxWidth: 640 }}>
                <ChatInput />
              </div>
            </motion.div>
          )}

          {activeTab === "chat" && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              style={{ display: "flex", flexDirection: "column", height: "100%", flex: 1 }}
            >
              <ChatPanel />
              <div style={{ padding: "20px 32px 32px" }}>
                <ChatInput />
              </div>
            </motion.div>
          )}

          {/* Add more tabs as needed */}
          {activeTab !== "home" && activeTab !== "chat" && (
            <motion.div
              key="fallback"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1, color: "var(--text-muted)" }}
            >
              <div style={{ textAlign: "center" }}>
                <Brain size={48} style={{ marginBottom: 16, opacity: 0.2 }} />
                <p>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} view coming soon</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ── Right Panel ───────────────────── */}
      <aside
        className="dashboard-panel"
        style={{
          background: "var(--bg-secondary)",
          borderLeft: "1px solid var(--border-subtle)",
          padding: 20,
          display: "flex",
          flexDirection: "column",
          gap: 24,
          overflowY: "auto"
        }}
      >
        <AITimeline />

        <div className="card" style={{ marginTop: "auto" }}>
          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 12 }}>
            System Status
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { label: "LangGraph Orchestrator", status: "online" },
              { label: "Memory Layer", status: "online" },
              { label: "Voice Pipeline", status: "standby" },
              { label: "Agent Pool (5)", status: "online" },
            ].map((s) => (
              <div key={s.label} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 12 }}>
                <span style={{ color: "var(--text-secondary)" }}>{s.label}</span>
                <span className={`badge ${s.status === "online" ? "badge-green" : "badge-amber"}`}>
                  {s.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}

