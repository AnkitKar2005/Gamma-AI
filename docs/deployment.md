# Gamma AI — Deployment Guide

## Local Development

### Infrastructure (Docker)
```bash
cd infra
docker compose up -d
# Starts: PostgreSQL (5432), Redis (6379), ChromaDB (8000)
```

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens: http://localhost:3000
```

## Production (Docker Compose)

```bash
# Set environment variables
export JWT_SECRET="your-secret"
export OPENAI_API_KEY="sk-..."

cd infra
docker compose -f docker-compose.prod.yml up --build -d
# Nginx serves on port 80
```

## Cloud Deployment

### Frontend → Vercel
1. Connect repo to Vercel
2. Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` env vars
3. Deploy

### Backend → Railway
1. Create new Railway project
2. Add PostgreSQL and Redis add-ons
3. Deploy backend with `Dockerfile.backend`
4. Set all env vars in Railway dashboard

## Monitoring

- Health check: `GET /health`
- Structured JSON logging via `structlog`
- WebSocket connection count in health response

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection failed | Check Docker containers: `docker compose ps` |
| WebSocket won't connect | Verify CORS origins include frontend URL |
| LLM responses empty | Check `OPENAI_API_KEY` is set |
| Voice not working | Verify both `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` |
