import sys
import re
import json
from typing import Any, Dict, Tuple

from src.tfidf import TFIDF
from src.retriever import search
from src.semantic import Semantic


class Cache:
    """Local cache for index objects and query results."""

    def __init__(self) -> None:
        self.query_cached: Dict[str, Any] = {}
        self.tfidf: TFIDF | None = None
        self.semantic: Semantic | None = None

    def get_index(
        self, index_path: str, embeddings_path: str
    ) -> Tuple[TFIDF, Semantic]:
        """Load and cache index objects from disk."""
        if self.tfidf is None:
            self.tfidf = TFIDF()
            self.tfidf.load(index_path)
        if self.semantic is None:
            self.semantic = Semantic()
            self.semantic.load(embeddings_path)
        return self.tfidf, self.semantic

    def cache_query(
        self,
        chunks_path: str,
        index_path: str,
        embeddings_path: str,
        query: str,
        k: int,
    ) -> Any:
        """Search with caching for repeated query requests."""
        clean_query = re.sub(r"[^\w\s]", "", query)
        key = f"{' '.join(clean_query.lower().strip())}-{k}"
        if key in self.query_cached:
            print("query founded in cache")
            return self.query_cached[key]

        print("Cache miss. Searching...")
        tfidf, semantic = self.get_index(index_path, embeddings_path)
        result = search(chunks_path, tfidf, semantic, query, k)
        self.query_cached[key] = result
        return self.query_cached[key]

    def save(self, path: str) -> None:
        """Serialize the cached query map to disk."""
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.query_cached, file, indent=2)

    def load(self, path: str) -> None:
        """Load a saved cache map from disk."""
        try:
            with open(path, "r", encoding="utf-8") as file:
                self.query_cached = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)
