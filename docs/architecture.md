# Gamma AI — System Architecture

## Overview

Gamma AI is a multi-agent AI operating system built on a layered architecture:

1. **Presentation Layer** — Next.js 15 frontend with real-time WebSocket communication
2. **Gateway Layer** — FastAPI with JWT auth, CORS, and request routing
3. **AI Layer** — LangGraph state machine orchestrating intent classification → memory retrieval → agent routing → response generation
4. **Agent Layer** — Specialized agents (Memory, Data, Decision, Trigger, Voice) with independent execution
5. **Data Layer** — Three-tier memory (Redis → ChromaDB → PostgreSQL)

## LangGraph Orchestrator

```
START → classify_intent → retrieve_memory → [conditional routing]
    ├── weather/crypto/news → data_agent → generate_response → END
    ├── memory_query/store  → memory_agent → generate_response → END
    ├── decision           → decision_agent → generate_response → END
    └── general            → generate_response → END
```

## Memory System

| Tier | Store | Purpose | TTL |
|------|-------|---------|-----|
| Short-term | Redis | Recent conversation turns | 2 hours |
| Semantic | ChromaDB | Embedding-based similarity search | Permanent |
| Long-term | PostgreSQL | User profiles, preferences, facts | Permanent |

## Real-time Protocol

WebSocket message envelope:
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "type": "chat_message|chat_token|chat_done|agent_event|notification|...",
  "payload": {},
  "ts": "ISO-8601"
}
```

Heartbeat: Server pings every 30s, disconnects stale connections after 90s.
Reconnect: Client uses exponential backoff (1s → 2s → 4s → 8s → 16s max).

## Voice Pipeline

```
Audio Capture → WebSocket → Whisper STT → LangGraph → ElevenLabs TTS → WebSocket → Audio Playback
```

Supports barge-in: client detects microphone activity during TTS playback and sends `interrupt` message.
