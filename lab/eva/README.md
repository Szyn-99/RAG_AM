*This project has been created as part of the 42 curriculum by nodoulah.*

# RAG

## Description

This repository implements a Retrieval-Augmented Generation (RAG) system for searching and answering questions over source code and Markdown content. The goal is to index a local repository, split content into retrieval-friendly chunks, combine lexical and semantic retrieval, and generate answers from the best retrieved documents.

The project is built as a small research pipeline that demonstrates hybrid retrieval methods, chunking strategies, and answer generation using retrieved context.

## System Architecture

The system is composed of the following components:

- `src/chunker.py`: splits code and Markdown content into smaller chunks for retrieval.
- `src/tfidf.py`: builds a lexical TF-IDF index over chunk text.
- `src/semantic.py`: computes semantic embeddings using SentenceTransformers.
- `src/hybrid_retrieval.py`: ranks TF-IDF and semantic results using Reciprocal Rank Fusion (RRF).
- `src/retriever.py`: orchestrates query execution, retrieves top candidates, and formats results.
- `src/cache.py`: caches index objects and repeated query results.
- `src/indexer.py`: builds and saves both TF-IDF and semantic indexes.
- `src/generator.py`: loads data, generates answers using retrieved context, and supports dataset answer generation.
- `src/incremental.py`: detects changed files and updates chunks/indexes incrementally.
- `src/api.py`: exposes HTTP endpoints for search and answer requests.
- `src/__main__.py`: command-line interface powered by `fire`.

### Interaction flow

1. The chunker reads source files and Markdown files.
2. The indexer builds a TF-IDF index and semantic embeddings from chunk text.
3. A query is executed through the retriever, which calls TF-IDF and semantic search.
4. Hybrid ranking fuses both results into an ordered candidate list.
5. The generator uses retrieved chunks as context to produce an answer.
6. The API and CLI expose the search and answer functionality to users.

## Chunking Strategy

The chunking approach is designed to preserve natural document structure:

- Python files are segmented at `def` and `class` boundaries. This keeps function or class blocks together as meaningful retrieval units.
- Markdown files are segmented using top-level headings (`#`). Each section becomes a chunk that maintains coherent context.
- Chunks are capped by a configurable `max_chunk_size` to avoid overly large retrieval units.

This strategy balances granularity and context preservation, making retrieval results more relevant.

## Retrieval Method

Retrieval is hybrid and composed of two complementary algorithms:

- **TF-IDF**: a classical lexical ranking algorithm implemented in `src/tfidf.py`. TF-IDF scores chunks based on term frequency and inverse document frequency.
- **Semantic search**: embedding-based retrieval implemented in `src/semantic.py` using SentenceTransformers. It ranks chunks by cosine similarity in embedding space.
- **Reciprocal Rank Fusion (RRF)**: `src/hybrid_retrieval.py` merges TF-IDF and semantic rankings. RRF improves robustness by combining different ranking signals rather than relying on a single model.

The final retrieval set is the best mix of lexical precision and semantic relevance.

## Performance Analysis

The project includes an evaluation path to compute recall metrics.

- `src/evaluation.py` calculates `recall@k` by comparing retrieved chunks against ground-truth source references.
- `k` controls how many top results are considered for recall.
- System performance depends on corpus size, embedding generation time, and model inference cost.

In practice, TF-IDF is fast for lexical lookups, while semantic indexing requires more time and memory for embedding generation. The hybrid method is intended to better capture relevance than either method alone.

## Design Decisions

Key implementation choices include:

- Using a hybrid retrieval pipeline to combine lexical and semantic strengths.
- Chunking by code definitions and Markdown headings for coherent retrieval units.
- Requiring `k` as an explicit query parameter to avoid hidden defaults and make top-k behavior clear.
- Supporting incremental indexing to reduce reprocessing for changed files.
- Exposing both CLI and HTTP API interfaces for flexibility.

## Challenges Faced

The main challenges addressed in this project were:

- Preserving retrieval context while chunking code and documentation.
- Combining different ranking sources without losing useful candidates.
- Handling large semantic embedding files and keeping a usable cache.
- Ensuring the system remained understandable for a peer review setting.

Solutions included using RRF fusion, caching index objects, and keeping chunk boundaries aligned with natural document structure.

## Instructions

### Setup

1. Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
make install
```

### Indexing

Build chunks, TF-IDF index, and semantic embeddings:

```bash
make run ARG=" index --max_chunk_size=2000"
```

### Incremental indexing

Update the index only for changed files:

```bash
make run ARG="incremental_index --max_chunk_size=2000"
```

### Search

Run a search query:

```bash
make run ARG="search --query='What is TF-IDF?' --k=10"
```

### Answer

Generate an answer from retrieved chunks:

```bash
make run ARG="answer --query='How does hybrid retrieval work?' --k=10"
```

### Dataset search

Search over a dataset and save results:

```bash
make run ARG="search_dataset --dataset_path='data/datasets/AnsweredQuestions/dataset_docs_public.json' --k=10"
```

### Evaluate results

Compute recall metrics for a search result file:

```bash
make run ARG="evaluate --student_search_results_path='data/output/search_results/dataset_docs_public.json' --dataset_path='data/datasets/AnsweredQuestions/dataset_docs_public.json' --k=10"
```

### Run HTTP API

Launch the API server:

```bash
make run ARG=" http_api"
```

Then open:

- `http://127.0.0.1:8000/search?query=...&k=10`
- `http://127.0.0.1:8000/answer?query=...&k=10`

## Example Usage

Search example:

```bash
make run ARG="search --query='Find function definitions' --k=5"
```

API example:

```bash
curl "http://127.0.0.1:8000/search?query=source+code&k=5"
```

## Resources

- TF-IDF algorithm: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- SentenceTransformers: https://www.sbert.net/
- FastAPI documentation: https://fastapi.tiangolo.com/
- Python `fire`: https://github.com/google/python-fire
- RAG overview: https://www.retrieval-augmented-generation.com/

### AI usage

AI was used to help document the project and structure the README content clearly. The AI assisted in:

- defining instructions and usage examples
- summarizing the retrieval and chunking strategy

