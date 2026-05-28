"use client";

import { create } from "zustand";

export type TabId = "home" | "chat" | "memory" | "timeline" | "notifications" | "settings";

interface ViewState {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
}

export const useViewStore = create<ViewState>((set) => ({
  activeTab: "home",
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
