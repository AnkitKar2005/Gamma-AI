"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Home,
  MessageCircle,
  Brain,
  Clock,
  Bell,
  Settings,
  Sparkles,
} from "lucide-react";

import { useViewStore, type TabId } from "@/store/viewStore";

const navItems: { icon: any; label: string; id: TabId }[] = [
  { icon: Home, label: "Home", id: "home" },
  { icon: MessageCircle, label: "Chat", id: "chat" },
  { icon: Brain, label: "Memory", id: "memory" },
  { icon: Clock, label: "Timeline", id: "timeline" },
  { icon: Bell, label: "Alerts", id: "notifications" },
  { icon: Settings, label: "Settings", id: "settings" },
];

export default function Sidebar() {
  const { activeTab, setActiveTab } = useViewStore();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <aside
      className="dashboard-sidebar"
      style={{
        background: "var(--bg-secondary)",
        borderRight: "1px solid var(--border-subtle)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "20px 0",
        zIndex: 50,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Logo */}
      <motion.div
        style={{
          width: 40,
          height: 40,
          borderRadius: "12px",
          background: "conic-gradient(from 0deg, #8b5cf6, #d946ef, #3b82f6, #8b5cf6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 32,
          cursor: "pointer",
          boxShadow: "var(--shadow-glow)",
        }}
        animate={{ rotate: isHovered ? 360 : 0 }}
        transition={{ duration: 2, ease: "easeInOut" }}
      >
        <Sparkles size={20} color="white" />
      </motion.div>

      {/* Navigation */}
      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 4,
          flex: 1,
          width: "100%",
          padding: "0 12px",
        }}
      >
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          const Icon = item.icon;

          return (
            <motion.button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                position: "relative",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 48,
                height: 48,
                borderRadius: "var(--radius-md)",
                border: "none",
                background: isActive ? "rgba(139, 92, 246, 0.15)" : "transparent",
                color: isActive ? "var(--accent-purple)" : "var(--text-muted)",
                cursor: "pointer",
                transition: "all var(--transition-fast)",
              }}
              title={item.label}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  style={{
                    position: "absolute",
                    left: -12,
                    width: 3,
                    height: 24,
                    borderRadius: "0 4px 4px 0",
                    background: "var(--gradient-primary)",
                  }}
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <Icon size={20} />
            </motion.button>
          );
        })}
      </nav>

      {/* Bottom avatar */}
      <div
        style={{
          width: 36,
          height: 36,
          borderRadius: "var(--radius-full)",
          background: "var(--gradient-primary)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 14,
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        G
      </div>
    </aside>
  );
}
