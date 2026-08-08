import sys
import json
import math
import re
from typing import List, Tuple


class TFIDF:
    """Lexical text retrieval model that ranks documents with
    TF-IDF scoring."""
    def __init__(self) -> None:
        self.corpus: list = []
        self.idf: dict = {}
        self.STOPWORDS: set = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "be",
            "been",
            "being",
            "have",
            "has",
            "do",
            "does",
            "did",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "and",
            "or",
            "but",
            "if",
            "not",
            "this",
            "that",
            "it",
            "its",
            "what",
            "how",
            "which",
            "who",
            "when",
            "where",
            "why",
            "all",
            "each",
            "both",
            "more",
            "so",
            "than",
            "too",
            "very",
            "just",
            "no",
        }

    def tokenize(self, text: str) -> List[str]:
        """Normalize text into a token list for TF-IDF indexing."""
        clean_text = re.sub(r"[^\w\s]", " ", text)
        words = clean_text.lower().split()
        tokens = [w for w in words if w not in self.STOPWORDS]
        if not tokens:
            return words
        return tokens

    def index(self, texts: List[str]) -> None:
        """Build a TF-IDF index from the provided documents."""
        self.corpus = [self.tokenize(text) for text in texts]
        counter = {}
        for doc in self.corpus:
            see = set()
            for word in doc:
                if word not in see:
                    if word not in counter:
                        counter[word] = 1
                    else:
                        counter[word] += 1
                    see.add(word)
        for term, df in counter.items():
            self.idf[term] = math.log(len(self.corpus) / df)

    def calculate_tfidf(self, tf: float, idf: float, total_word: int) -> float:
        """Compute a normalized TF-IDF weight for a term in a document."""
        if total_word == 0 or tf == 0:
            return 0.0
        tf_sub = 1 + math.log(tf)
        normalized_tf = tf_sub / (1 + math.log(total_word))
        return normalized_tf * idf

    def searcher(self, query: str, k: int) -> List[Tuple[float, int]]:
        """Search the indexed corpus using TF-IDF similarity scores."""
        token_query = self.tokenize(query)
        scores = []
        i = 0
        for doc in self.corpus:
            score: float = 0.0
            for word in token_query:
                tf = doc.count(word)
                idf = self.idf.get(word, 0)
                score += self.calculate_tfidf(tf, idf, len(doc))
            scores.append((score, i))
            i += 1
        result = sorted(scores, reverse=True)
        return result[:k]

    def save(self, path: str) -> None:
        """Persist the TF-IDF index data to a JSON file."""
        data = {"idf": self.idf, "corpus": self.corpus}
        with open(path, "w", encoding="utf-8", errors="ignore") as file:
            json.dump(data, file, indent=2)

    def load(self, path: str) -> None:
        """Load previously saved TF-IDF index data from a JSON file."""
        try:
            with open(path, "r") as file:
                content = json.load(file)
            self.idf = content["idf"]
            self.corpus = content["corpus"]
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)
