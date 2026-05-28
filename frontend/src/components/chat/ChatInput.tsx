"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Mic, MicOff } from "lucide-react";
import { useChatStore } from "@/store/chatStore";
import { useOrbStore } from "@/store/orbStore";

interface ChatInputProps {
  onSend?: (message: string) => void;
}

export default function ChatInput({ onSend }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [voiceMode, setVoiceMode] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const isLoading = useChatStore((s) => s.isLoading);
  const addMessage = useChatStore((s) => s.addMessage);
  const setLoading = useChatStore((s) => s.setLoading);
  const setOrbState = useOrbStore((s) => s.setState);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;

    // Add user message
    addMessage("user", trimmed);
    setLoading(true);
    setOrbState("thinking");
    setValue("");

    // Notify parent (WebSocket send)
    onSend?.(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleVoice = () => {
    setVoiceMode(!voiceMode);
    if (!voiceMode) {
      setOrbState("listening");
    } else {
      setOrbState("idle");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        padding: "16px 24px",
        borderTop: "1px solid var(--border-subtle)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: 10,
          padding: "8px 8px 8px 16px",
          borderRadius: "var(--radius-xl)",
          background: "var(--bg-card)",
          border: "1px solid var(--border-subtle)",
          transition: "all var(--transition-fast)",
        }}
      >
        <textarea
          ref={inputRef}
          id="chat-input-main"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isLoading ? "Gamma is responding..." : "Ask Gamma anything..."
          }
          disabled={isLoading}
          rows={1}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            outline: "none",
            color: "var(--text-primary)",
            fontSize: 14,
            resize: "none",
            lineHeight: 1.5,
            maxHeight: 120,
            opacity: isLoading ? 0.5 : 1,
          }}
        />

        {/* Voice toggle */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleVoice}
          style={{
            width: 36,
            height: 36,
            borderRadius: "var(--radius-full)",
            background: voiceMode ? "rgba(59, 130, 246, 0.15)" : "transparent",
            border: `1px solid ${voiceMode ? "rgba(59, 130, 246, 0.3)" : "var(--border-subtle)"}`,
            color: voiceMode ? "var(--accent-blue)" : "var(--text-muted)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
          title={voiceMode ? "Stop voice" : "Voice input"}
        >
          {voiceMode ? <MicOff size={16} /> : <Mic size={16} />}
        </motion.button>

        {/* Send button */}
        <motion.button
          whileHover={value.trim() ? { scale: 1.1 } : {}}
          whileTap={value.trim() ? { scale: 0.9 } : {}}
          onClick={handleSend}
          disabled={!value.trim() || isLoading}
          style={{
            width: 36,
            height: 36,
            borderRadius: "var(--radius-full)",
            background: value.trim() && !isLoading
              ? "var(--gradient-primary)"
              : "var(--bg-hover)",
            border: "none",
            color: value.trim() && !isLoading ? "white" : "var(--text-muted)",
            cursor: value.trim() && !isLoading ? "pointer" : "default",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            boxShadow: value.trim() && !isLoading ? "var(--shadow-glow)" : "none",
          }}
          title="Send message"
        >
          <Send size={16} />
        </motion.button>
      </div>

      <p
        style={{
          fontSize: 11,
          color: "var(--text-muted)",
          textAlign: "center",
          marginTop: 8,
        }}
      >
        Shift+Enter for new line · Gamma can make mistakes
      </p>
    </motion.div>
  );
}
