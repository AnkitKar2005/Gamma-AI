"""Gamma AI — ChromaDB Semantic Memory Store."""

from typing import Optional

import structlog

from config import get_settings

logger = structlog.get_logger()


class ChromaMemory:
    """Semantic memory using ChromaDB for embedding storage and similarity search."""

    def __init__(self):
        self._client = None
        self._collection = None

    async def connect(self) -> None:
        """Connect to ChromaDB."""
        try:
            import chromadb

            settings = get_settings()
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )
            self._collection = self._client.get_or_create_collection(
                name="gamma_memories",
                metadata={"hnsw:space": "cosine"},
            )
            await logger.ainfo("ChromaMemory connected")
        except Exception as e:
            await logger.awarning("ChromaMemory unavailable", error=str(e))
            self._client = None

    async def embed_and_store(
        self,
        text: str,
        metadata: Optional[dict] = None,
        doc_id: Optional[str] = None,
    ) -> Optional[str]:
        """Embed text via OpenAI and upsert to ChromaDB."""
        if self._collection is None:
            return None
        try:
            from services.llm import llm_service
            from uuid import uuid4

            doc_id = doc_id or str(uuid4())

            # Get embedding from OpenAI
            embedding = await llm_service.embed(text)
            if embedding is None:
                # Fallback: let ChromaDB handle embedding
                self._collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata or {}],
                )
            else:
                self._collection.upsert(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata or {}],
                )

            return doc_id
        except Exception as e:
            await logger.awarning("Failed to embed and store", error=str(e))
            return None

    async def semantic_search(
        self, query: str, top_k: int = 5, user_id: Optional[str] = None
    ) -> list[dict]:
        """Search for semantically similar memories."""
        if self._collection is None:
            return []
        try:
            from services.llm import llm_service

            # Get query embedding
            query_embedding = await llm_service.embed(query)

            where_filter = {"user_id": user_id} if user_id else None

            if query_embedding:
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter,
                )
            else:
                results = self._collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_filter,
                )

            # Flatten results
            memories = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    memories.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                        "id": results["ids"][0][i] if results.get("ids") else None,
                    })

            return memories
        except Exception as e:
            await logger.awarning("Semantic search failed", error=str(e))
            return []


# Global singleton
chroma_memory = ChromaMemory()
