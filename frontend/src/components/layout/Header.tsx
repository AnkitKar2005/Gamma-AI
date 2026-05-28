"use client";

import { useState, useEffect } from "react";
import { Bell, Wifi, WifiOff } from "lucide-react";
import NotificationPanel from "@/components/notifications/NotificationPanel";

export default function Header() {
  const [dateStr, setDateStr] = useState("");
  const [timeStr, setTimeStr] = useState("");
  const [connectionStatus, setConnectionStatus] = useState<
    "connected" | "disconnected" | "connecting"
  >("disconnected");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setDateStr(
        now.toLocaleDateString("en-US", {
          weekday: "long",
          month: "long",
          day: "numeric",
          year: "numeric",
        })
      );
      setTimeStr(
        now.toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        })
      );
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Simulate connection status — will be driven by useWebSocket in Phase 2
  useEffect(() => {
    setConnectionStatus("connecting");
    const timer = setTimeout(() => setConnectionStatus("connected"), 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <header
      className="dashboard-header glass"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 28px",
        borderBottom: "1px solid var(--border-subtle)",
      }}
    >
      {/* Left: Date & Time */}
      <div style={{ display: "flex", flexDirection: "column" }}>
        <span
          style={{
            fontSize: 13,
            color: "var(--text-muted)",
            fontWeight: 500,
            letterSpacing: "0.02em",
          }}
        >
          {dateStr}
        </span>
        <span
          style={{
            fontSize: 22,
            fontWeight: 700,
            background: "var(--gradient-primary)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            lineHeight: 1.2,
          }}
        >
          {timeStr}
        </span>
      </div>

      {/* Center: Greeting */}
      <div
        style={{
          fontSize: 15,
          color: "var(--text-secondary)",
          fontWeight: 500,
        }}
      >
        Welcome back to{" "}
        <span className="gradient-text" style={{ fontWeight: 700 }}>
          Gamma AI
        </span>
      </div>

      {/* Right: Status & Notifications */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {/* Connection Status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 12px",
            borderRadius: "var(--radius-full)",
            background: "var(--bg-card)",
            border: "1px solid var(--border-subtle)",
            fontSize: 12,
            color: "var(--text-secondary)",
          }}
        >
          {connectionStatus === "connected" ? (
            <Wifi size={14} color="var(--accent-green)" />
          ) : (
            <WifiOff size={14} color="var(--accent-red)" />
          )}
          <span className={`status-dot ${connectionStatus}`} />
          <span style={{ textTransform: "capitalize" }}>{connectionStatus}</span>
        </div>

        {/* Notification Panel */}
        <NotificationPanel />
      </div>
    </header>
  );
}
