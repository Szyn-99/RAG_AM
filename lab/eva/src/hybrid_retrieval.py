def rrf(
    ifidf_result: list[int],
    semantic_result: list[int],
    k: int,
) -> list[int]:
    """Fuse TFIDF and semantic rankings using Reciprocal Rank Fusion (RRF).

    Args:
        ifidf_result: Ranked document IDs from TFIDF retrieval.
        semantic_result: Ranked document IDs from semantic retrieval.
        k: Number of top documents to return.

    Returns:
        A list of the top `k` document IDs ranked by their combined RRF scores.
    """
    scores: dict[int, float] = {}
    for score, idx in enumerate(ifidf_result):
        scores[idx] = scores.get(idx, 0.0) + 1 / (score + 60)
    for score, idx in enumerate(semantic_result):
        scores[idx] = scores.get(idx, 0.0) + 1 / (score + 60)
    final_score = sorted(scores, key=lambda idx: scores[idx], reverse=True)
    return final_score[:k]
