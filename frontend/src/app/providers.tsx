"use client";

import { ReactNode } from "react";

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Client-side providers wrapper.
 * Zustand stores don't need a Provider — they work out of the box.
 * This component is here for future provider additions (e.g., theme, auth).
 */
export default function Providers({ children }: ProvidersProps) {
  return <>{children}</>;
}
