"""Data models used by the RAG pipeline.

This module defines Pydantic models for chunk sources, questions,
search results, and answers.
"""

import sys
import uuid

try:
    from pydantic import BaseModel, Field
except (ModuleNotFoundError, ImportError):
    print("Module not installed")
    sys.exit(1)
from typing import List


class MinimalSource(BaseModel):
    """A retrieved source location inside a document chunk."""

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """A question that has not yet been answered."""

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """A dataset question with sources and an answer."""

    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """A dataset containing a list of RAG questions."""

    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """Search result metadata returned for a query."""

    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """A search result that includes an answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """A stored student search results collection."""

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """A stored search results collection with generated answers."""

    search_results: List[MinimalAnswer]
    k: int
