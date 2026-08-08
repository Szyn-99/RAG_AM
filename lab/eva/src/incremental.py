"""Support incremental re-indexing when source files change."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

from src.chunker import chunk_markedown, chunk_python_code
from src.indexer import indexer


def save_times(repo_path: str, output_path: str) -> None:
    """Save modification timestamps for Python and Markdown files."""
    folder = Path(repo_path)
    save_files: Dict[str, float] = {}
    for file in folder.rglob("*"):
        if file.suffix in {".py", ".md"}:
            save_files[str(file)] = os.path.getmtime(file)
    with open(output_path, "w", encoding="utf-8") as output_handle:
        json.dump(save_files, output_handle, indent=2)


def get_changed(repo_path: str, times_path: str) -> List[str]:
    """Return the list of changed source files since the last timestamp
    snapshot."""
    with open(times_path, "r", encoding="utf-8") as time_handle:
        times_files = json.load(time_handle)
    folder = Path(repo_path)
    save_files: List[str] = []
    for entry in folder.rglob("*"):
        if entry.suffix in {".py", ".md"}:
            saved_time = times_files.get(str(entry), 0)
            if saved_time != os.path.getmtime(entry):
                save_files.append(str(entry))
    return save_files


def incremental(
    repo_path: str,
    times_path: str,
    chunk_path: str,
    index_path: str,
    embeddings_path: str,
    max_chunk_size: int = 2000,
) -> None:
    """Update the stored index and chunk database for changed files."""
    with open(
        chunk_path,
        "r",
        encoding="utf-8",
    ) as input_handle:
        old_chunks = json.load(input_handle)

    saved_files = get_changed(repo_path, times_path)
    clean_chunks: List[dict] = [
        chunk
        for chunk in old_chunks
        if chunk["file_path"] in saved_files
    ]

    if not saved_files:
        print("No files changed. Index is up to date!")
        sys.exit(1)

    for file in saved_files:
        if file.endswith(".py"):
            chunk = chunk_python_code(file, max_chunk_size)
            clean_chunks += chunk
        elif file.endswith(".md"):
            chunk = chunk_markedown(file, max_chunk_size)
            clean_chunks += chunk
    if not clean_chunks:
        print("No chunks found")
        sys.exit(1)
    with open(chunk_path, "w", encoding="utf-8") as f:
        json.dump(clean_chunks, f, indent=2)
    indexer(chunk_path, index_path, embeddings_path)
    save_times(repo_path, times_path)
