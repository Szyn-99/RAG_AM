"""indexing and retrieval stage."""
import re
from typing import List, Any, Tuple
import os
from src.chunking_data import chunk_repository
import json
from tqdm import tqdm
from rank_bm25 import BM25Okapi
import pickle
from src.classes_types import Chunk, MinimalSource
import numpy


CHUNKS_PATH: str = "data/processed/chunks/chunks.json"
BM25_INDEX_PATH: str = "data/processed/bm25_index/bm25.pkl"
TOKENS_LISTS: str = "data/processed/bm25_index/tokenslists.pkl"


def my_tokenizer(text: str) -> List[str]:
    """
    Tokenize and normalize input text.

    The tokenizer splits snake_case and CamelCase identifiers,
    converts the text to lowercase, removes punctuation, and
    returns a list of normalized tokens.

    Args:
        text: Input text to tokenize.

    Returns:
        A list of normalized tokens.
    """
    text = text.replace("_", " ")

    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)

    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)

    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text)

    tokens_list: List = [elem for elem in text.split() if len(elem) > 1]

    return tokens_list


def build_the_indexed_stock(repo_path: str = "data/raw/vllm-0.10.1",
                            max_chunk_size: int = 2000) -> None:
    """
    Build and store the BM25 index for a repository.

    The repository is chunked, tokenized, indexed with BM25,
    and the resulting chunks and index are saved to disk.

    Args:
        repo_path: Path to the repository to index.
        max_chunk_size: Maximum size of each generated chunk.

    Returns:
        None.
    """
    print(f"\nStart Indexing The Repo: {repo_path}\n")

    os.makedirs("data/processed/chunks", exist_ok=True)
    os.makedirs("data/processed/bm25_index", exist_ok=True)

    all_chunks_result: List[Chunk] = chunk_repository(repo_path,
                                                      max_chunk_size)
    print(f"THERE ARE {len(all_chunks_result)} chunks THAT CREATED NOW.\n")

    print(f"\nStart Saving Them(chunks) To The File Path -> {CHUNKS_PATH}")
    list_of_chunks_dictionries: List = []
    for chunk_obj in all_chunks_result:
        list_of_chunks_dictionries.append(chunk_obj.model_dump())

    with open(CHUNKS_PATH, "w") as file:
        as_string: str = json.dumps(
            list_of_chunks_dictionries,
            indent=2, ensure_ascii=False)
        file.write(as_string)
        print("AER SAVED.\n")

    print("START BUILDING BM25 index...")
    tokens_list_result: List = []
    for chunk_obj in tqdm(all_chunks_result,
                          desc="THE TOKENIZER progress bar"):
        lst: List = my_tokenizer(chunk_obj.content)
        tokens_list_result.append(lst)

    bm25_result: Any = BM25Okapi(tokens_list_result)
    binarries_bytes: Any = pickle.dumps(bm25_result)

    with open(BM25_INDEX_PATH, "wb") as file:
        file.write(binarries_bytes)
        print(f"\n\nCREATED BM25 FILE DATABASE. path {BM25_INDEX_PATH}\n")

    binarries_bytes = pickle.dumps(tokens_list_result)
    with open(TOKENS_LISTS, "wb") as file:
        file.write(binarries_bytes)
        print(f"CREATED CACHE MEMORY FILE FOR TOKENS. path {TOKENS_LISTS}\n")

    print()
    print("="*62)
    print("complete! data saved under root: data/processed/...")
    print("="*62)
    print()


def load_indexed_data_from_disk() -> Tuple[BM25Okapi, List[Chunk]]:
    """
    Load the BM25 index and chunk metadata from disk.

    Returns:
        A tuple containing the BM25 index and the list of indexed
        chunks.

    Raises:
        FileNotFoundError: If the indexed data does not exist.
    """
    if not os.path.exists(BM25_INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        raise FileNotFoundError("Program Still Does not Have any indexed data")

    with open(BM25_INDEX_PATH, "rb") as file:
        bm25: Any = pickle.loads(file.read())

    with open(CHUNKS_PATH, "r") as file:
        chunks_as_string: str = file.read()
        list_of_chunks: List = json.loads(chunks_as_string)

    list_of_chunks_obj: List = []
    for ch_dict in list_of_chunks:
        list_of_chunks_obj.append(Chunk(**ch_dict))

    return bm25, list_of_chunks_obj


def retrieval(query: str, bm25: BM25Okapi,
              chunks: List[Chunk], k: int = 10) -> List[MinimalSource]:
    """
    Retrieve the top-k most relevant source locations.

    The query is tokenized, scored using the BM25 index, and the
    highest-ranked unique source locations are returned.

    Args:
        query: User search query.
        bm25: Loaded BM25 index.
        chunks: Indexed repository chunks.
        k: Maximum number of results to return.

    Returns:
        A list containing the top-k retrieved source locations.
    """
    tokenize_query: List[str] = my_tokenizer(query)
    scores: Any = bm25.get_scores(tokenize_query)

    best_k_indexes: Any = numpy.argsort(scores)[::-1][:k]

    result: List = []
    scores_cache: set = set()

    for idx in best_k_indexes:
        o_chk: Chunk = chunks[idx]

        build_key: Tuple = (o_chk.file_path,
                            o_chk.first_character_index,
                            o_chk.last_character_index)

        if build_key in scores_cache:
            continue
        scores_cache.add(build_key)

        obj: MinimalSource = MinimalSource(
            file_path=o_chk.file_path,
            first_character_index=o_chk.first_character_index,
            last_character_index=o_chk.last_character_index)

        result.append(obj)

    return result[:k]
