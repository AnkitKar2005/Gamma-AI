"""Gamma AI — FastAPI Application Entry Point."""

import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from models.database import close_db, init_db
from models.schemas import HealthResponse, SessionResponse
from auth.jwt import create_token
from routes.chat import router as chat_router
from routes.memory import router as memory_router
from routes.voice import router as voice_router
from websocket.manager import manager as ws_manager
from websocket.handler import MessageHandler
from websocket.events import event_bus

# ── Structured Logging ────────────────────────

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()


# ── Lifespan ──────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()
    await logger.ainfo("Starting Gamma AI", env=settings.app_env)

    # Initialize database tables (dev only — use Alembic in prod)
    try:
        await init_db()
        await logger.ainfo("Database initialized")
    except Exception as e:
        await logger.awarning("Database init skipped (not connected)", error=str(e))

    # Connect event bus to Redis
    try:
        await event_bus.connect(settings.redis_url)
        await logger.ainfo("Event bus connected")
    except Exception as e:
        await logger.awarning("Event bus running in local mode", error=str(e))

    yield

    # Shutdown
    await event_bus.close()
    await close_db()
    await logger.ainfo("Gamma AI shutdown complete")


# ── App Factory ───────────────────────────────

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Multi-agent AI operating system with real-time streaming, voice I/O, and persistent memory.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request ID Middleware ─────────────
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # ── Routes ────────────────────────────
    app.include_router(chat_router)
    app.include_router(memory_router)
    app.include_router(voice_router)

    # ── WebSocket ─────────────────────────
    msg_handler = MessageHandler(ws_manager)

    @app.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        """Main WebSocket endpoint for real-time communication."""
        await msg_handler.handle_connection(websocket, session_id)

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health_check():
        """System health check endpoint."""
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            services={
                "api": "running",
                "websocket": f"{ws_manager.active_connections} connections",
                "database": "pending",
                "redis": "pending",
                "chromadb": "pending",
            },
        )

    @app.post("/api/v1/session", response_model=SessionResponse, tags=["auth"])
    async def create_session():
        """Auto-issue a new session with JWT token."""
        token, session_id = create_token()
        return SessionResponse(session_id=session_id, token=token)

    return app


# ── Application Instance ─────────────────────

app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
