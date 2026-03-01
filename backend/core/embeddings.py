"""Gemini embedding helper that targets the v1 endpoints."""

from __future__ import annotations

import hashlib
import math
from typing import List

from google import genai
from langchain_core.embeddings import Embeddings


class GeminiEmbeddings(Embeddings):
    """Lightweight wrapper around google-genai embeddings for LangChain."""

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._fallback_model = "models/embedding-001"
        self._local_dimensions = 256
        self._client = genai.Client(api_key=api_key)

    @staticmethod
    def _extract_values(entry) -> List[float]:  # type: ignore[override]
        embedding = getattr(entry, "embedding", entry)
        return list(embedding.values)

    def _embed(self, text: str, task_type: str) -> List[float]:
        try:
            response = self._client.models.embed_content(
                model=self._model,
                contents=text,
                config={"task_type": task_type},
            )
            return self._extract_values(response.embedding)
        except Exception as exc:
            message = str(exc)
            model_missing = (
                "404" in message
                and "NOT_FOUND" in message
                and "embed" in message.lower()
            )
            if not model_missing:
                raise

            try:
                response = self._client.models.embed_content(
                    model=self._fallback_model,
                    contents=text,
                    config={"task_type": task_type},
                )
                return self._extract_values(response.embedding)
            except Exception:
                return self._local_embed(text)

    def _local_embed(self, text: str) -> List[float]:
        vector = [0.0] * self._local_dimensions
        tokens = [token for token in text.lower().split() if token]
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self._local_dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:  # type: ignore[override]
        if not texts:
            return []
        return [self._embed(text, "RETRIEVAL_DOCUMENT") for text in texts]

    def embed_query(self, text: str) -> List[float]:  # type: ignore[override]
        return self._embed(text, "RETRIEVAL_QUERY")
