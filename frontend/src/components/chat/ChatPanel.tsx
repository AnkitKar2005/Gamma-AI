"use client";

import { useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useChatStore } from "@/store/chatStore";
import ChatMessage from "./ChatMessage";

export default function ChatPanel() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);

  const scrollRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [userScrolled, setUserScrolled] = useState(false);

  // Auto-scroll to bottom unless user has scrolled up
  useEffect(() => {
    if (!userScrolled && scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, userScrolled]);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const atBottom = scrollHeight - scrollTop - clientHeight < 80;
    setUserScrolled(!atBottom);
  };

  if (messages.length === 0) return null;

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      style={{
        flex: 1,
        overflowY: "auto",
        padding: "0 24px",
        maxHeight: "100%",
      }}
    >
      <AnimatePresence initial={false}>
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </AnimatePresence>

      {/* Loading indicator */}
      {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "12px 0",
            color: "var(--text-muted)",
            fontSize: 13,
          }}
        >
          <Loader2
            size={16}
            style={{ animation: "rotate 1s linear infinite" }}
          />
          Gamma is thinking...
        </motion.div>
      )}

      {/* Scroll anchor */}
      <div ref={scrollRef} />
    </div>
  );
}
