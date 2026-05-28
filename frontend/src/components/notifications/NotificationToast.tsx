"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Info, AlertTriangle, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";
import type { Notification } from "@/types";

interface NotificationToastProps {
  notification: Notification;
  onDismiss: (id: string) => void;
}

const priorityConfig = {
  info: { icon: Info, color: "#3b82f6", bg: "rgba(59, 130, 246, 0.1)", border: "rgba(59, 130, 246, 0.2)" },
  warning: { icon: AlertTriangle, color: "#f59e0b", bg: "rgba(245, 158, 11, 0.1)", border: "rgba(245, 158, 11, 0.2)" },
  critical: { icon: AlertCircle, color: "#ef4444", bg: "rgba(239, 68, 68, 0.1)", border: "rgba(239, 68, 68, 0.2)" },
};

export default function NotificationToast({ notification, onDismiss }: NotificationToastProps) {
  const config = priorityConfig[notification.priority];
  const Icon = config.icon;

  // Auto-dismiss
  useEffect(() => {
    const timeout = notification.priority === "critical" ? 10000 : 5000;
    const timer = setTimeout(() => onDismiss(notification.id), timeout);
    return () => clearTimeout(timer);
  }, [notification.id, notification.priority, onDismiss]);

  return (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.95 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      style={{
        background: config.bg,
        backdropFilter: "blur(16px)",
        border: `1px solid ${config.border}`,
        borderRadius: "var(--radius-lg)",
        padding: "14px 16px",
        maxWidth: 360,
        boxShadow: "var(--shadow-lg)",
        display: "flex",
        gap: 12,
        alignItems: "flex-start",
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: "var(--radius-md)",
          background: `${config.color}20`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <Icon size={16} color={config.color} />
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 2 }}>
          {notification.title}
        </p>
        <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
          {notification.body}
        </p>
        {notification.action_url && (
          <a
            href={notification.action_url}
            style={{
              fontSize: 12,
              color: config.color,
              fontWeight: 600,
              marginTop: 6,
              display: "inline-block",
            }}
          >
            View Details →
          </a>
        )}
      </div>

      <button
        onClick={() => onDismiss(notification.id)}
        style={{
          background: "transparent",
          border: "none",
          color: "var(--text-muted)",
          cursor: "pointer",
          padding: 4,
          flexShrink: 0,
        }}
      >
        <X size={14} />
      </button>
    </motion.div>
  );
}
