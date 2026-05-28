"""Gamma AI — Chat REST API Routes."""

from fastapi import APIRouter, Depends

from auth.jwt import get_current_session
from models.schemas import ChatRequest, ChatResponse, ChatMessage, ChatMessageRole

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: dict = Depends(get_current_session),
):
    """Send a chat message and receive a response.

    This is the REST fallback for non-WebSocket clients.
    In production, this will route through the LangGraph orchestrator.
    """
    session_id = session.get("sub", "anonymous")

    # Phase 1: Echo-style placeholder — will be replaced by LangGraph in Phase 3
    response_message = ChatMessage(
        role=ChatMessageRole.ASSISTANT,
        content=f"👋 Gamma AI received your message: \"{request.message}\". "
                f"AI orchestration will be connected in Phase 3.",
    )

    return ChatResponse(
        message=response_message,
        session_id=session_id,
        conversation_id=request.conversation_id or "default",
    )
