/**
 * Gamma AI — Notification Store (Zustand)
 */

import { create } from "zustand";
import type { Notification } from "@/types";

interface NotificationStore {
  notifications: Notification[];
  addNotification: (notification: Notification) => void;
  markRead: (id: string) => void;
  clearAll: () => void;
  unreadCount: () => number;
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],

  addNotification: (notification) =>
    set((s) => ({
      notifications: [notification, ...s.notifications],
    })),

  markRead: (id) =>
    set((s) => ({
      notifications: s.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
    })),

  clearAll: () => set({ notifications: [] }),

  unreadCount: () => get().notifications.filter((n) => !n.read).length,
}));
