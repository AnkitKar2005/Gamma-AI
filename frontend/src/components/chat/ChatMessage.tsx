"use client";

import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { Bot, User, Copy, Check } from "lucide-react";
import { useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/types";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === "assistant";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: "flex",
        gap: 12,
        padding: "12px 0",
        alignItems: "flex-start",
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: "var(--radius-md)",
          background: isAssistant ? "var(--gradient-primary)" : "var(--bg-hover)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        {isAssistant ? (
          <Bot size={16} color="white" />
        ) : (
          <User size={16} color="var(--text-secondary)" />
        )}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 4,
          }}
        >
          <span
            style={{
              fontSize: 13,
              fontWeight: 600,
              color: isAssistant ? "var(--text-accent)" : "var(--text-primary)",
            }}
          >
            {isAssistant ? "Gamma AI" : "You"}
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          {message.isStreaming && (
            <span className="badge badge-purple">Streaming</span>
          )}
        </div>

        <div
          style={{
            fontSize: 14,
            lineHeight: 1.65,
            color: "var(--text-primary)",
          }}
          className="chat-content"
        >
          {isAssistant ? (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : (
            <p>{message.content}</p>
          )}
          {message.isStreaming && (
            <motion.span
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 0.8, repeat: Infinity }}
              style={{
                display: "inline-block",
                width: 6,
                height: 16,
                background: "var(--accent-purple)",
                borderRadius: 2,
                marginLeft: 2,
                verticalAlign: "text-bottom",
              }}
            />
          )}
        </div>

        {/* Actions */}
        {isAssistant && !message.isStreaming && (
          <div style={{ marginTop: 8 }}>
            <button
              onClick={handleCopy}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
                fontSize: 11,
                color: "var(--text-muted)",
                background: "transparent",
                border: "none",
                cursor: "pointer",
                padding: "4px 8px",
                borderRadius: "var(--radius-sm)",
                transition: "all var(--transition-fast)",
              }}
              title="Copy response"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
