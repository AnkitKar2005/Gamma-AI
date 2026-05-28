"""Gamma AI — PostgreSQL Long-Term Memory Store."""

from typing import Any, Optional

import structlog

from config import get_settings

logger = structlog.get_logger()


class PostgresMemory:
    """Long-term memory using PostgreSQL for user profiles and persistent records."""

    async def get_user_profile(self, session_id: str) -> Optional[dict]:
        """Get user profile by session ID."""
        try:
            from models.database import get_session_factory, User
            from sqlalchemy import select

            factory = get_session_factory()
            async with factory() as session:
                stmt = select(User).where(User.session_id == session_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    return {
                        "id": str(user.id),
                        "session_id": user.session_id,
                        "display_name": user.display_name,
                        "preferences": user.preferences or {},
                    }
                return None
        except Exception as e:
            await logger.awarning("Failed to get user profile", error=str(e))
            return None

    async def update_preference(self, session_id: str, key: str, value: Any) -> None:
        """Upsert a user preference."""
        try:
            from models.database import get_session_factory, User
            from sqlalchemy import select, update
            from uuid import uuid4

            factory = get_session_factory()
            async with factory() as session:
                stmt = select(User).where(User.session_id == session_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    prefs = user.preferences or {}
                    prefs[key] = value
                    user.preferences = prefs
                else:
                    user = User(
                        id=uuid4(),
                        session_id=session_id,
                        preferences={key: value},
                    )
                    session.add(user)

                await session.commit()
        except Exception as e:
            await logger.awarning("Failed to update preference", error=str(e))

    async def store_memory_record(
        self, user_id: str, content: str, memory_type: str = "general"
    ) -> Optional[str]:
        """Store a long-term memory record."""
        try:
            from models.database import get_session_factory, MemoryRecord as DBMemory
            from uuid import uuid4

            record_id = uuid4()
            factory = get_session_factory()
            async with factory() as session:
                record = DBMemory(
                    id=record_id,
                    user_id=user_id,
                    content=content,
                    memory_type=memory_type,
                )
                session.add(record)
                await session.commit()
                return str(record_id)
        except Exception as e:
            await logger.awarning("Failed to store memory record", error=str(e))
            return None

    async def get_memory_records(
        self, user_id: str, memory_type: Optional[str] = None, limit: int = 20
    ) -> list[dict]:
        """Retrieve memory records."""
        try:
            from models.database import get_session_factory, MemoryRecord as DBMemory
            from sqlalchemy import select

            factory = get_session_factory()
            async with factory() as session:
                stmt = select(DBMemory).where(DBMemory.user_id == user_id)
                if memory_type:
                    stmt = stmt.where(DBMemory.memory_type == memory_type)
                stmt = stmt.order_by(DBMemory.created_at.desc()).limit(limit)

                result = await session.execute(stmt)
                records = result.scalars().all()
                return [
                    {
                        "id": str(r.id),
                        "content": r.content,
                        "memory_type": r.memory_type,
                        "importance": r.importance,
                        "created_at": str(r.created_at),
                    }
                    for r in records
                ]
        except Exception as e:
            await logger.awarning("Failed to get memory records", error=str(e))
            return []


# Global singleton
postgres_memory = PostgresMemory()
