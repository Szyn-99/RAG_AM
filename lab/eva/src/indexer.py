"""Indexing utilities for the RAG pipeline.

This module loads chunked documents and builds both lexical and semantic
indexes for retrieval.
"""

import json
import sys
from typing import Any

from src.tfidf import TFIDF
from src.semantic import Semantic


def load_chunk(path: str) -> Any:
    """Load chunk metadata from a JSON file.

    Args:
        path: Path to the JSON chunks file.

    Returns:
        The parsed JSON content representing document chunks.
    """
    with open(path, "r") as file:
        try:
            chunks = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)
    return chunks


def indexer(chunks_path: str, index_path: str, embeddings_path: str) -> None:
    """Build TFIDF and semantic indexes from chunked texts.

    Args:
        chunks_path: Path to the chunk JSON file.
        index_path: Output path for the TFIDF index JSON file.
        embeddings_path: Output path for the semantic embeddings file.
    """
    chunks = load_chunk(chunks_path)
    corpus = [chunk["text"] for chunk in chunks]
    retriever_tfidf = TFIDF()
    retriever_tfidf.index(corpus)
    retriever_tfidf.save(index_path)
    retriever_semantic = Semantic()
    retriever_semantic.index(corpus)
    retriever_semantic.save(embeddings_path)
