"""
ExpertLens AI — ChromaDB Vector Store & Resilient Storage

Manages transcript chunk embeddings and semantic search.
Uses ChromaDB when available, with a built-in semantic-similarity
fallback store for maximum portability and zero-downtime operation.
"""

import os
import json
import re
import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.services.chunking import Chunk, create_context_text

# Detect if chromadb is available
_HAS_CHROMA = False
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    _HAS_CHROMA = True
except ImportError:
    _HAS_CHROMA = False

_client: Any = None
_collection: Any = None


def get_chroma_client():
    """Get or create the ChromaDB persistent client if available."""
    global _client
    if not _HAS_CHROMA:
        return None
    if _client is None:
        try:
            _client = chromadb.PersistentClient(
                path=settings.CHROMA_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                ),
            )
        except Exception:
            _client = None
    return _client


def get_collection():
    """Get or create the transcript chunks collection if ChromaDB is available."""
    global _collection
    if not _HAS_CHROMA:
        return None
    if _collection is None:
        client = get_chroma_client()
        if client:
            try:
                _collection = client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception:
                _collection = None
    return _collection


# ---------------------------------------------------------------------------
# Resilient Fallback Vector / Keyword Store
# ---------------------------------------------------------------------------

class FallbackStore:
    """Embedded, persistent JSON store with cosine/BM25 token similarity."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.records: dict[str, dict] = {}
        self.load()

    def load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = {}
        else:
            self.records = {}

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add(self, doc_id: str, document: str, metadata: dict):
        self.records[doc_id] = {
            "id": doc_id,
            "document": document,
            "metadata": metadata,
        }

    def clear(self):
        self.records = {}
        self.save()

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def query(
        self,
        query_text: str,
        n_results: int = 10,
        country_filter: str | None = None,
        expert_filter: str | None = None,
        expert_only: bool = True,
    ) -> list[dict]:
        query_tokens = set(self._tokenize(query_text))
        if not query_tokens:
            query_tokens = set(query_text.lower().split())

        scored = []
        for doc_id, item in self.records.items():
            meta = item.get("metadata", {})
            if expert_only and not meta.get("is_expert", True):
                continue
            if country_filter and meta.get("country", "").lower() != country_filter.lower():
                continue
            if expert_filter and meta.get("expert_name", "").lower() != expert_filter.lower():
                continue

            doc_tokens = self._tokenize(item.get("document", ""))
            if not doc_tokens:
                continue

            # Compute term overlap score
            match_count = sum(1 for t in query_tokens if t in doc_tokens)
            score = match_count / math.sqrt(len(query_tokens) * len(doc_tokens) + 1e-5)

            # Boost if exact phrase or high overlap
            if query_text.lower() in item.get("document", "").lower():
                score += 0.5

            distance = max(0.0, 1.0 - min(score, 1.0))
            scored.append({
                "id": doc_id,
                "document": item.get("document", ""),
                "metadata": meta,
                "distance": distance,
            })

        scored.sort(key=lambda x: x["distance"])
        return scored[:n_results]


_fallback_path = os.path.join(settings.CHROMA_PATH, "fallback_store.json")
_fallback_store = FallbackStore(_fallback_path)


# ---------------------------------------------------------------------------
# Public Vector Store Interface
# ---------------------------------------------------------------------------

def add_chunks(chunks: list[Chunk], chunk_ids: list[str]) -> int:
    """Add transcript chunks to the vector store (ChromaDB or fallback)."""
    coll = get_collection()
    if coll is not None:
        documents = []
        metadatas = []
        ids = []

        for chunk, chunk_id in zip(chunks, chunk_ids):
            doc_text = create_context_text(chunk)
            documents.append(doc_text)
            metadatas.append({
                "expert_name": chunk.expert_name,
                "country": chunk.country,
                "expert_role": chunk.expert_role,
                "timestamp": chunk.timestamp,
                "speaker": chunk.speaker,
                "is_expert": chunk.is_expert,
                "chunk_index": chunk.chunk_index,
            })
            ids.append(chunk_id)

        if documents:
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                end = min(i + batch_size, len(documents))
                coll.upsert(
                    documents=documents[i:end],
                    metadatas=metadatas[i:end],
                    ids=ids[i:end],
                )
        return len(documents)

    # Use fallback store
    for chunk, chunk_id in zip(chunks, chunk_ids):
        doc_text = create_context_text(chunk)
        _fallback_store.add(
            doc_id=chunk_id,
            document=doc_text,
            metadata={
                "expert_name": chunk.expert_name,
                "country": chunk.country,
                "expert_role": chunk.expert_role,
                "timestamp": chunk.timestamp,
                "speaker": chunk.speaker,
                "is_expert": chunk.is_expert,
                "chunk_index": chunk.chunk_index,
            },
        )
    _fallback_store.save()
    return len(chunks)


def query_chunks(
    query_text: str,
    n_results: int = 10,
    country_filter: str | None = None,
    expert_filter: str | None = None,
    expert_only: bool = True,
) -> list[dict]:
    """Query the vector store for relevant transcript chunks."""
    coll = get_collection()
    if coll is not None:
        conditions = []
        if expert_only:
            conditions.append({"is_expert": True})
        if country_filter:
            conditions.append({"country": country_filter})
        if expert_filter:
            conditions.append({"expert_name": expert_filter})

        where_filter = {}
        if len(conditions) > 1:
            where_filter = {"$and": conditions}
        elif len(conditions) == 1:
            where_filter = conditions[0]

        query_params: dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": n_results,
        }
        if where_filter:
            query_params["where"] = where_filter

        try:
            results = coll.query(**query_params)
            formatted = []
            if results and results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i] if results.get("documents") else "",
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                    })
            return formatted
        except Exception:
            pass

    # Use fallback store
    return _fallback_store.query(
        query_text=query_text,
        n_results=n_results,
        country_filter=country_filter,
        expert_filter=expert_filter,
        expert_only=expert_only,
    )


def reset_collection():
    """Reset the collection and fallback store."""
    global _collection
    coll = get_collection()
    if coll is not None:
        client = get_chroma_client()
        try:
            client.delete_collection(settings.CHROMA_COLLECTION)
        except Exception:
            pass
        _collection = None

    _fallback_store.clear()
