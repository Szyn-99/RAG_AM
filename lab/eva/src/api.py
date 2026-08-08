"""HTTP API wrapper for RAG search and answer endpoints."""

import os
import sys

from typing import Any, Dict, List
try:
    from fastapi import FastAPI, HTTPException
except (ModuleNotFoundError, ImportError):
    print("Module not installed")
    sys.exit(1)
from src.cache import Cache
from src.generator import genrate_answer, load_chunk, load_model

CHUNKS_PATH = "data/processed/chunks.json"
INDEX_PATH = "data/processed/tfidf_index.json"
EMBEDDINGS_PATH = "data/processed/embeddings.pt"
CACHE_PATH = "data/processed/query_cache.json"

cache = Cache()
if os.path.exists(CACHE_PATH):
    cache.load(CACHE_PATH)


app = FastAPI()


@app.get("/")
def root() -> str:
    """Return a short API homepage description."""
    return "/search  → find relevant chunks | /answer  → generate answer"


@app.get("/search")
def search(query: str, k: int) -> Dict[str, List[Dict[str, Any]]]:
    """Search for relevant chunks from the indexed corpus."""
    try:
        if not os.path.exists(CHUNKS_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {CHUNKS_PATH}",
            )
        if not os.path.exists(INDEX_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {INDEX_PATH}",
            )
        if not os.path.exists(EMBEDDINGS_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {EMBEDDINGS_PATH}",
            )
        if k <= 0:
            raise HTTPException(
                status_code=400,
                detail="k must be > 0",
            )
        if not query or not query.strip():
            raise HTTPException(
                status_code=400,
                detail="query cannot be empty",
            )
        result = cache.cache_query(
            CHUNKS_PATH,
            INDEX_PATH,
            EMBEDDINGS_PATH,
            query,
            k,
        )
        cache.save(CACHE_PATH)
        return {"result": [dict(r) for r in result]}
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/answer")
def answer(query: str, k: int) -> Dict[str, str]:
    """Generate an answer from retrieved chunks for a single query."""
    try:
        if not os.path.exists(CHUNKS_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {CHUNKS_PATH}",
            )
        if not os.path.exists(INDEX_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {INDEX_PATH}",
            )
        if not os.path.exists(EMBEDDINGS_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found at {EMBEDDINGS_PATH}",
            )
        if k <= 0:
            raise HTTPException(
                status_code=400,
                detail="k must be > 0",
            )
        if not query or not query.strip():
            raise HTTPException(
                status_code=400,
                detail="query cannot be empty",
            )
        pipe = load_model()
        chunks_retriever = cache.cache_query(
            CHUNKS_PATH,
            INDEX_PATH,
            EMBEDDINGS_PATH,
            query,
            k,
        )
        all_chunks = load_chunk(CHUNKS_PATH)
        answer_text = genrate_answer(pipe, query, all_chunks, chunks_retriever)
        return {"answer": answer_text}
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
