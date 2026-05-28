/**
 * Gamma AI — Orb State Store (Zustand)
 */

import { create } from "zustand";
import type { OrbState } from "@/types";

interface OrbStore {
  state: OrbState;
  setState: (newState: OrbState) => void;
}

// Valid state transitions
const validTransitions: Record<OrbState, OrbState[]> = {
  idle: ["listening", "thinking", "error"],
  listening: ["thinking", "idle", "error"],
  thinking: ["speaking", "idle", "error"],
  speaking: ["idle", "listening", "error"],
  error: ["idle"],
};

export const useOrbStore = create<OrbStore>((set, get) => ({
  state: "idle",

  setState: (newState) => {
    const current = get().state;
    const allowed = validTransitions[current];
    if (allowed?.includes(newState) || current === newState) {
      set({ state: newState });
    }
  },
}));
