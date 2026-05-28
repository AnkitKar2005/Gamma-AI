/**
 * Gamma AI — Timeline Store (Zustand)
 */

import { create } from "zustand";
import type { AgentEvent } from "@/types";

interface TimelineStore {
  events: AgentEvent[];
  addEvent: (event: AgentEvent) => void;
  clearEvents: () => void;
}

const MAX_EVENTS = 100;

export const useTimelineStore = create<TimelineStore>((set) => ({
  events: [],

  addEvent: (event) =>
    set((s) => ({
      events: [event, ...s.events].slice(0, MAX_EVENTS),
    })),

  clearEvents: () => set({ events: [] }),
}));
