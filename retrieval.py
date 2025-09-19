"""Retrieval layer backed by LlamaIndex with a keyword fallback."""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

from faq_loader import load_faq_entries
from honeyhive import trace

logger = logging.getLogger(__name__)

try:
    from llama_index.core import Document, VectorStoreIndex
    from llama_index.embeddings.openai import OpenAIEmbedding
    LLAMA_AVAILABLE = True
except ImportError as exc:
    Document = None  # type: ignore
    VectorStoreIndex = None  # type: ignore
    OpenAIEmbedding = None  # type: ignore
    MockEmbedding = None  # type: ignore
    LLAMA_AVAILABLE = False
    logger.warning("LlamaIndex not available: %s", exc)


class FAQRetriever:
    """Thin wrapper around LlamaIndex to serve FAQ snippets."""

    def __init__(
        self,
        faq_entries: Optional[List[Dict[str, str]]] = None,
        use_llamaindex: bool = True,
    ) -> None:
        self.faq_entries = faq_entries or load_faq_entries()
        self._retriever = None
        self.use_llamaindex = use_llamaindex and LLAMA_AVAILABLE

        if self.use_llamaindex and VectorStoreIndex and Document:
            try:
                documents = [
                    Document(
                        text=(
                            f"Category: {entry['category']}\n"
                            f"Title: {entry['title']}\n"
                            f"Answer: {entry['body']}"
                        ),
                        metadata=entry,
                    )
                    for entry in self.faq_entries
                ]

                # Use OpenAI embeddings if API key is set, else fallback to mock
                if os.getenv("OPENAI_API_KEY") and OpenAIEmbedding:
                    embed_model = OpenAIEmbedding(model="text-embedding-3-small")
                    logger.info("Using OpenAIEmbedding for FAQ retrieval")
                elif MockEmbedding:
                    embed_model = MockEmbedding(embed_dim=1536)
                    logger.info("Using MockEmbedding for FAQ retrieval")
                else:
                    raise RuntimeError("No embedding model available")

                index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
                self._retriever = index.as_retriever(similarity_top_k=1)
                logger.info(
                    "Initialized LlamaIndex retriever with %s FAQ entries",
                    len(documents),
                )
            except Exception as exc:
                logger.warning(
                    "Failed to initialize LlamaIndex (%s). Falling back to keyword search.",
                    exc,
                )
                self.use_llamaindex = False
        if not self.use_llamaindex:
            logger.info("Using keyword fallback retriever.")

    @trace
    def retrieve(self, query: str, category: Optional[str] = None) -> Dict[str, str]:
        """Return the FAQ entry that best matches the query."""
        if self.use_llamaindex and self._retriever is not None:
            try:
                nodes = self._retriever.retrieve(query)
                if nodes:
                    return dict(nodes[0].metadata)
            except Exception as exc:
                logger.warning("LlamaIndex retrieval failed (%s). Falling back.", exc)

        # --- Keyword fallback ---
        lowered_query = query.lower()
        best_score = -1
        best_entry: Dict[str, str] = self.faq_entries[0]
        for entry in self.faq_entries:
            score = 0
            if category and entry.get("category") == category:
                score += 5
            title = entry.get("title", "").lower()
            body = entry.get("body", "").lower()
            for token in [
                "crash", "bug", "slow", "lag",
                "feature", "request", "love", "thanks",
                "billing", "charge", "login", "password",
                "mode", "dark"
            ]:
                if token in lowered_query and token in (title + body):
                    score += 2
            if any(word in lowered_query for word in title.split()):
                score += 1
            if any(word in lowered_query for word in body.split()):
                score += 0.5
            if score > best_score:
                best_score = score
                best_entry = entry
        return best_entry


__all__ = ["FAQRetriever", "LLAMA_AVAILABLE"]
