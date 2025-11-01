"""
Embedding utilities for representing documents in semantic space.

This module uses OpenAI's embeddings API via the official SDK v1
(`from openai import OpenAI`). It follows the project's configuration
pattern: API keys are loaded from `config.json` through `Config`.
"""

from __future__ import annotations

from typing import List, Optional, Sequence
import logging

from openai import OpenAI

from ._config import Config

_logger = logging.getLogger(__name__)


# Default embedding model for this project
EMBEDDING_MODEL: str = "text-embedding-3-small"
#EMBEDDING_MODEL: str = "text-embedding-3-large"


def embed_document(
    document: str,
    *,
    config: Optional[Config] = None,
    client: Optional[OpenAI] = None,
) -> List[float]:
    """
    Compute a single-vector embedding for the given document using
    OpenAI's `text-embedding-3-small` model.

    Args:
        document: The text to embed.
        config: Optional `Config`. If not provided, `Config.load()` is used.
        client: Optional preconfigured `OpenAI` client (useful for testing).

    Returns:
        Embedding vector as a list of floats.

    Raises:
        TypeError: If `document` is not a string.
        ValueError: If the API returns no embedding data.
    """
    if not isinstance(document, str):
        raise TypeError("document must be a str")

    cfg = config or Config.load()
    cli = client or OpenAI(api_key=cfg.api_key)

    _logger.debug("Requesting embedding (model=%s, len=%d)", EMBEDDING_MODEL, len(document))
    resp = cli.embeddings.create(model=EMBEDDING_MODEL, input=document)

    if not resp.data or not resp.data[0].embedding:
        raise ValueError("No embedding returned by API")

    return resp.data[0].embedding  # type: ignore[return-value]


def embed_documents(
    documents: Sequence[str],
    *,
    config: Optional[Config] = None,
    client: Optional[OpenAI] = None,
) -> List[List[float]]:
    """
    Compute embeddings for a batch of documents.

    Args:
        documents: Sequence of texts to embed.
        config: Optional `Config`. If not provided, `Config.load()` is used.
        client: Optional preconfigured `OpenAI` client.

    Returns:
        A list of embedding vectors (one per input document).
    """
    if any(not isinstance(doc, str) for doc in documents):
        raise TypeError("all documents must be str")

    cfg = config or Config.load()
    cli = client or OpenAI(api_key=cfg.api_key)

    _logger.debug(
        "Requesting %d embeddings (model=%s)", len(documents), EMBEDDING_MODEL
    )
    resp = cli.embeddings.create(model=EMBEDDING_MODEL, input=list(documents))
    return [d.embedding for d in resp.data]
