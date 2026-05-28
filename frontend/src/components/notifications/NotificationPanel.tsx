"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Bell, Check, Trash2, X } from "lucide-react";
import { useNotificationStore } from "@/store/notificationStore";
import { useState } from "react";

export default function NotificationPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const notifications = useNotificationStore((s) => s.notifications);
  const markRead = useNotificationStore((s) => s.markRead);
  const clearAll = useNotificationStore((s) => s.clearAll);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <>
      {/* Trigger Button */}
      <button
        id="notification-panel-btn"
        onClick={() => setIsOpen(true)}
        style={{
          position: "relative",
          background: "var(--bg-card)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)",
          padding: 10,
          cursor: "pointer",
          color: "var(--text-secondary)",
        }}
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span
            style={{
              position: "absolute",
              top: -2,
              right: -2,
              width: 16,
              height: 16,
              borderRadius: "var(--radius-full)",
              background: "var(--accent-red)",
              fontSize: 10,
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>

      {/* Slide-out Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              style={{
                position: "fixed",
                inset: 0,
                background: "rgba(0, 0, 0, 0.4)",
                zIndex: 90,
              }}
            />

            {/* Panel */}
            <motion.div
              initial={{ x: 400 }}
              animate={{ x: 0 }}
              exit={{ x: 400 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              style={{
                position: "fixed",
                top: 0,
                right: 0,
                width: 380,
                height: "100vh",
                background: "var(--bg-secondary)",
                borderLeft: "1px solid var(--border-subtle)",
                zIndex: 100,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
              }}
            >
              {/* Header */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "16px 20px",
                  borderBottom: "1px solid var(--border-subtle)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <h2 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>
                    Notifications
                  </h2>
                  {unreadCount > 0 && <span className="badge badge-purple">{unreadCount} new</span>}
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    onClick={clearAll}
                    style={{
                      background: "transparent",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "var(--radius-sm)",
                      padding: "4px 8px",
                      cursor: "pointer",
                      color: "var(--text-muted)",
                      fontSize: 11,
                      display: "flex",
                      alignItems: "center",
                      gap: 4,
                    }}
                  >
                    <Trash2 size={12} /> Clear
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    style={{
                      background: "transparent",
                      border: "none",
                      cursor: "pointer",
                      color: "var(--text-muted)",
                      padding: 4,
                    }}
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>

              {/* Notification List */}
              <div style={{ flex: 1, overflowY: "auto", padding: 12 }}>
                {notifications.length === 0 ? (
                  <div style={{ textAlign: "center", padding: 40, color: "var(--text-muted)", fontSize: 13 }}>
                    <Bell size={32} style={{ marginBottom: 12, opacity: 0.3 }} />
                    <p>No notifications yet</p>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {notifications.map((n) => (
                      <motion.div
                        key={n.id}
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="card"
                        style={{
                          padding: 12,
                          opacity: n.read ? 0.6 : 1,
                          cursor: "pointer",
                        }}
                        onClick={() => markRead(n.id)}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                          <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                            {n.title}
                          </span>
                          {!n.read && (
                            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent-purple)", flexShrink: 0, marginTop: 4 }} />
                          )}
                        </div>
                        <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.4 }}>
                          {n.body}
                        </p>
                        <span style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
                          {new Date(n.timestamp).toLocaleTimeString()}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
