*This project has been created as part of the 42 curriculum by hel-achh*

# RAG Against the Machine

## Description

RAG Against the Machine is a Retrieval-Augmented Generation (RAG) system that indexes a software repository and answers natural language questions about its contents.

The project combines document chunking, lexical retrieval using the BM25 ranking algorithm, and a Large Language Model (LLM) to generate answers based only on the retrieved repository content.

The main objective is to build an efficient retrieval pipeline capable of locating the most relevant code or documentation fragments before passing them to the language model for answer generation.

---

# System Architecture
The RAG pipeline is composed of the following stages:

    Repository
        │
        ▼
    Chunking
        │
        ▼
    Tokenization
        │
        ▼
    BM25 Index
        │
────────────────

    User Question
        │
        ▼
    Tokenization
        │
        ▼
    BM25 Retrieval
        │
        ▼
    Top-K Chunks
        │
        ▼
    Prompt Builder
        │
        ▼
      Qwen3
        │
        ▼
    Generated Answer

The RAG pipeline consists: indexing and question answering.

During indexing, repository files are segmented into chunks, tokenized, and stored in a BM25 index.

When a user submits a question, the query is tokenized using the same preprocessing pipeline. BM25 retrieves the highest-ranked chunks, which are then provided as context to the Qwen3 language model. The model generates an answer based solely on the retrieved repository content.

---

# Chunking Strategy

The repository supports two chunking strategies.

## Python Files

Python source files are parsed using Python's Abstract Syntax Tree (AST).

Each top-level:

* Class
* Function
* Async Function

is extracted as an independent chunk.

Large functions exceeding the maximum chunk size are recursively split while preserving their source offsets.

Advantages:

* Keeps logical code units together.
* Improves retrieval quality.

---

## Text Files

Markdown and text files are divided according to:

* Markdown headings
* Paragraph boundaries

If a section exceeds the configured chunk size, it is split line by line until every chunk satisfies the size constraint.

---

# Retrieval Method

The retrieval stage uses the BM25 ranking algorithm implemented with the `rank_bm25` library.

The indexing process consists of:

1. Chunk repository files.
2. Normalize and tokenize every chunk.
3. Build a BM25 index.
4. Store:

   * chunks
   * BM25 index
   * tokens cache

For every query:

1. Normalize and tokenize the query.
2. Compute BM25 scores.
3. Rank every chunk.
4. Return the Top-K highest scoring chunks.


---

# Performance Analysis

The retrieval quality is evaluated using Recall@k.

The implemented metrics are:

* Recall@1
* Recall@3
* Recall@5
* Recall@10

The evaluation compares retrieved source locations against the reference dataset using Intersection over Union (IoU).

A retrieved source is considered correct when:

```
IoU ≥ 0.05
```

The evaluation script reports:

* Number of evaluated questions
* Recall@1
* Recall@3
* Recall@5
* Recall@10

## Evaluation Results

### Code Dataset :
| Metric | Score |
|--------|------:|
| Recall@1 | 0.370 |
| Recall@3 | 0.570 |
| Recall@5 | 0.640 |
| Recall@10 | 0.740 |

### Documentation Dataset :
| Metric | Score |
|--------|------:|
| Recall@1 | 0.570 |
| Recall@3 | 0.780 |
| Recall@5 | 0.840 |
| Recall@10 | 0.880 |
---

# Design Decisions

Several implementation choices were made during development.

### AST-based chunking

Python files are parsed with the AST module to preserve semantic boundaries.

### BM25 retrieval

BM25 was selected because:

* Fast indexing
* Strong lexical matching
* Excellent baseline retrieval performance

### Cached index

The BM25 index and tokenized corpus are serialized with Pickle to avoid rebuilding the index on every execution.

### Separate retrieval and generation

Retrieval and answer generation are implemented as independent stages, making the system easier to evaluate and extend.

### Trade-offs

Several trade-offs were considered during development:

- Smaller chunks improve retrieval precision but may lose important context.
- Larger chunks preserve more context but can reduce retrieval accuracy.
- Caching the indexed obj was good, but should be good with Retrieved From it.
- Create a good prompt for the model for get a good answer, avoiding the hallucination.
---

# Challenges Faced

Several challenges were encountered during development.

## Chunk size

Very small chunks lacked sufficient context.

Very large chunks reduced retrieval precision.

A balanced chunk size of approximately **2000 characters** produced the best results.

---

## Python parsing

If Some files contained syntax errors.
Solve it with: Fallback to text chunking whenever AST parsing fails.

---

## Duplicate retrievals

Multiple retrieved chunks sometimes pointed to identical source ranges.

Solution:

Duplicate source locations are filtered before returning the final Top-K results.

---

## Efficient indexing

Rebuilding the BM25 index for every execution was expensive.

Solution:
Store the BM25 index and token cache on disk after indexing.

---

# Instructions

## Requirements

* Python 3.10+
* uv

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Install dependencies:

```bash
uv sync

or can use Makefile
```

---

# Usage

## Build the index

```bash
uv run python3 -m src index
```

---

## Search

```bash
uv run python3 -m src search "What is vLLM?"
```

---

## Answer a question

```bash
uv run python3 -m src answer "What is vLLM?"
```

---

## Search an entire dataset

```bash
uv run python3 -m src search_dataset PATH_DATASET
```

---

## Generate answers

```bash
uv run python3 -m src answer_dataset PATH_SEARCH_RESULT
```

---

## Evaluate retrieval

```bash
uv run python3 -m src evaluate   STUDENT_RESULTS_PATH   DATASET_PATH
```

---

# Example Usage

Search:

```bash
uv run python3 -m src search "How does the scheduler work?"
```

Output:

```text
TOP 10 RETRIEVED RESULTS...

1. scheduler.py [1324:2198]
2. worker.py [540:1261]
...
```

Generate an answer:

```bash
uv run python3 -m src answer "How does the scheduler work?"
```

The system retrieves the most relevant repository chunks and uses the Qwen language model to generate an answer based on those sources.

---

# Resources

## Documentation

* Pydantic Documentation — https://pydantic.dev/docs/validation/latest/get-started/
* NumPy Documentation — https://numpy.org/
* rank_bm25 — https://en.wikipedia.org/wiki/Okapi_BM25
* RAG as concept : https://www.youtube.com/watch?v=J5HaXOTy16g&list=PLZ42ZUInDWC79Bw1K_tYQhUPfFRV7fy8v

---

# AI Usage

Artificial Intelligence tools (ChatGPT) were used as a learning assistant during this project.

AI was used for:

* Learn the BM25/tf-idf ranking algorithm.
* Understanding Python AST parsing.
* Improving code documentation.
* Reviewing README formatting.
