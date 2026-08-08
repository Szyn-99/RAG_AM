"""Semantic embedding support for the RAG pipeline."""

import sys
from typing import List

try:
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer, util
except (ImportError, ModuleNotFoundError):
    print("Module not installed")
    sys.exit(1)


class Semantic:
    """Semantic index wrapper using SentenceTransformers."""

    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings: np.ndarray | None = None

    def index(self, texts: List[str]) -> None:
        """Encode a list of texts into semantic vectors."""
        self.embeddings = self.model.encode(texts, show_progress_bar=True)

    def search(self, query: str, k: int) -> List[int]:
        """Search the semantic index for the top-k most similar entries."""
        assert self.embeddings is not None
        vector_query: np.ndarray = self.model.encode(query)
        score = util.cos_sim(vector_query, self.embeddings)
        np_result: np.ndarray = score.numpy()
        result: np.ndarray = np.argsort(np_result[0])[::-1][:k]
        return [int(x) for x in result]

    def save(self, path: str) -> None:
        """Save semantic embeddings to a file."""
        tensor = torch.from_numpy(self.embeddings)
        torch.save(tensor, path)

    def load(self, path: str) -> None:
        """Load semantic embeddings from a file."""
        tensor = torch.load(path)
        self.embeddings = tensor.numpy()
