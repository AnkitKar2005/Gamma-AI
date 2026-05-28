# Gamma AI — Intelligent Operating System

A production-grade, multi-agent AI platform with real-time streaming, voice I/O, persistent memory, and proactive notifications.

![Gamma AI](https://img.shields.io/badge/Gamma-AI-8b5cf6?style=for-the-badge) ![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square) ![LangGraph](https://img.shields.io/badge/LangGraph-0.4-purple?style=flat-square)

## Architecture

```
Frontend (Next.js 15) ←→ WebSocket ←→ FastAPI Gateway
                                          ↓
                                    LangGraph Orchestrator
                                    ↓         ↓         ↓
                              Memory Agent  Data Agent  Decision Agent
                              ↓    ↓    ↓
                           Redis  Postgres  ChromaDB
```

**5 Specialized Agents:**
- **Memory Agent** — Multi-tier memory (Redis short-term → ChromaDB semantic → Postgres long-term)
- **Data Agent** — Live weather, crypto, and news via external APIs
- **Decision Agent** — GPT-4o structured reasoning with confidence scores
- **Trigger Agent** — Background scheduler for proactive notifications
- **Voice Agent** — Whisper STT → Orchestrator → ElevenLabs TTS pipeline

## Quick Start

### Prerequisites
- Docker Desktop
- Node.js 20+
- Python 3.11+

### 1. Clone & Configure
```bash
cp .env.example backend/.env
cp .env.example frontend/.env.local
# Edit .env files with your API keys
```

### 2. Start Infrastructure
```bash
cd infra
docker compose up -d
```

### 3. Start Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🚀

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | GPT-4o chat + Whisper STT |
| `ELEVENLABS_API_KEY` | No | Text-to-speech |
| `OPENWEATHERMAP_API_KEY` | No | Weather data |
| `COINGECKO_API_KEY` | No | Crypto prices (free tier) |
| `NEWS_API_KEY` | No | News headlines |
| `JWT_SECRET` | Yes | JWT signing secret |
| `DATABASE_URL` | Yes | PostgreSQL connection |
| `REDIS_URL` | Yes | Redis connection |

## Project Structure

```
├── frontend/          # Next.js 15 + Tailwind + Framer Motion
│   ├── src/app/       # App Router pages
│   ├── src/components/# UI components (Orb, Chat, Timeline, Notifications)
│   ├── src/hooks/     # useWebSocket, useVoice, useStream
│   └── src/store/     # Zustand stores
├── backend/           # FastAPI + LangGraph
│   ├── agents/        # Memory, Data, Decision, Trigger, Voice
│   ├── orchestrator/  # LangGraph state machine
│   ├── memory/        # Redis, Postgres, ChromaDB stores
│   ├── services/      # LLM, STT, TTS wrappers
│   ├── tools/         # Weather, Crypto, News APIs
│   └── websocket/     # Connection manager + event bus
├── infra/             # Docker configs + Nginx
└── docs/              # Architecture, API, Deployment docs
```

## Production Deployment

```bash
cd infra
docker compose -f docker-compose.prod.yml up --build -d
```

## License

MIT
