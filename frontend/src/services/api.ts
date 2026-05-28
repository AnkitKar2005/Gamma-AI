/**
 * Gamma AI — REST API Client
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
  headers?: Record<string, string>;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", body, token, headers = {} } = options;

  const config: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // ── Health ────────────────────────────
  health: () => request<{ status: string; version: string }>("/health"),

  // ── Session ───────────────────────────
  createSession: () =>
    request<{ session_id: string; token: string }>("/api/v1/session", {
      method: "POST",
    }),

  // ── Chat ──────────────────────────────
  sendMessage: (message: string, token: string, sessionId?: string) =>
    request("/api/v1/chat/", {
      method: "POST",
      body: { message, session_id: sessionId },
      token,
    }),

  // ── Memory ────────────────────────────
  getMemories: (token: string) =>
    request("/api/v1/memory/", { token }),

  createMemory: (content: string, token: string) =>
    request("/api/v1/memory/", {
      method: "POST",
      body: { content },
      token,
    }),

  searchMemories: (query: string, token: string) =>
    request("/api/v1/memory/search", {
      method: "POST",
      body: { query },
      token,
    }),
};
