# Gamma AI — API Reference

## REST Endpoints

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with service statuses |
| `POST` | `/api/v1/session` | Create a new session (returns JWT + session_id) |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/` | Send a message, receive a response |

### Memory
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/memory/` | List memory records |
| `POST` | `/api/v1/memory/` | Create a memory record |
| `POST` | `/api/v1/memory/search` | Semantic search across memories |

### Voice
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/voice` | Upload audio, get text response |

## WebSocket

Connect: `ws://host/ws/{session_id}?token={jwt}`

### Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `chat_message` | Client → Server | User message |
| `chat_token` | Server → Client | Streaming response token |
| `chat_done` | Server → Client | Streaming complete |
| `voice_data` | Client → Server | Audio chunk (base64) |
| `agent_event` | Server → Client | Agent activity for timeline |
| `notification` | Server → Client | Proactive notification |
| `error` | Server → Client | Error message |
| `heartbeat` | Bidirectional | Keep-alive ping/pong |
| `ack` | Bidirectional | Message acknowledgment |
| `interrupt` | Client → Server | Cancel in-flight TTS |

## Authentication

Session-based JWT (auto-issued):
1. `POST /api/v1/session` → `{ session_id, token }`
2. Include token in `Authorization: Bearer <token>` header
3. For WebSocket: `ws://host/ws/{session_id}?token={jwt}`
