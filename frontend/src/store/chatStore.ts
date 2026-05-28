/**
 * Gamma AI — Chat Store (Zustand)
 */

import { create } from "zustand";
import type { ChatMessage, ChatRole } from "@/types";

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;

  addMessage: (role: ChatRole, content: string) => string;
  appendToken: (messageId: string, token: string) => void;
  completeMessage: (messageId: string) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,

  addMessage: (role, content) => {
    const id = crypto.randomUUID?.() ?? `${Date.now()}`;
    const message: ChatMessage = {
      id,
      role,
      content,
      timestamp: new Date().toISOString(),
      isStreaming: role === "assistant",
    };
    set((s) => ({ messages: [...s.messages, message] }));
    return id;
  },

  appendToken: (messageId, token) => {
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === messageId ? { ...m, content: m.content + token } : m
      ),
    }));
  },

  completeMessage: (messageId) => {
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === messageId ? { ...m, isStreaming: false } : m
      ),
      isLoading: false,
    }));
  },

  setLoading: (loading) => set({ isLoading: loading }),

  clearMessages: () => set({ messages: [], isLoading: false }),
}));
