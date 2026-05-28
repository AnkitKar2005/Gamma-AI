"""Gamma AI — Memory CRUD REST API Routes."""

from fastapi import APIRouter, Depends

from auth.jwt import get_current_session
from models.schemas import MemoryCreateRequest, MemoryRecord, MemorySearchRequest

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.get("/", response_model=list[MemoryRecord])
async def get_memories(
    session: dict = Depends(get_current_session),
    memory_type: str | None = None,
    limit: int = 20,
):
    """Retrieve memory records for the current session.

    Will be connected to PostgresMemory + ChromaMemory in Phase 3.
    """
    # Placeholder — return empty list until memory system is connected
    return []


@router.post("/", response_model=MemoryRecord)
async def create_memory(
    request: MemoryCreateRequest,
    session: dict = Depends(get_current_session),
):
    """Store a new memory record.

    Will be connected to memory system in Phase 3.
    """
    return MemoryRecord(
        content=request.content,
        memory_type=request.memory_type,
        importance=request.importance,
    )


@router.post("/search", response_model=list[MemoryRecord])
async def search_memories(
    request: MemorySearchRequest,
    session: dict = Depends(get_current_session),
):
    """Semantic search across memories.

    Will be connected to ChromaMemory in Phase 3.
    """
    return []
