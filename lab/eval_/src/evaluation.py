"""eval & recall at k part."""
from typing import Dict, List
from src.classes_types import (MinimalSource,
                               RagDataset,
                               StudentSearchResults,
                               AnsweredQuestion)


def is_pass_after_calculate(src_obj1: MinimalSource,
                            src_true_obj2: MinimalSource,
                            minimal_for_pass: float = 0.05) -> bool:
    """
    Determine whether two source locations match.

    The function computes the Intersection over Union (IoU) between two
    source ranges and returns whether the overlap satisfies the given
    threshold.

    Args:
        src_obj1: Retrieved source location.
        src_true_obj2: Ground-truth source location.
        minimal_for_pass: Minimum IoU required for a successful match.

    Returns:
        True if the IoU is greater than or equal to the threshold,
        otherwise False.
    """
    if src_obj1.file_path != src_true_obj2.file_path:
        return False

    start1: int = src_obj1.first_character_index
    end1: int = src_obj1.last_character_index

    start2: int = src_true_obj2.first_character_index
    end2: int = src_true_obj2.last_character_index

    s_inter: int = max(start1, start2)
    e_inter: int = min(end1, end2)

    if e_inter <= s_inter:
        return False

    len_intersection: int = e_inter - s_inter

    union: int = ((end1 - start1) + (end2 - start2)) - len_intersection
    if union == 0:
        return False

    iou: float = len_intersection / union

    return iou >= minimal_for_pass


def percent_in_k_retrives(retrieved_for_question: List[MinimalSource],
                          truth_base_data: List[MinimalSource],
                          k: int,
                          minimal_for_pass: float = 0.05) -> float:
    """
    Compute the recall for a single question at a given k.

    The function compares the top-k retrieved sources with the
    ground-truth sources and returns the fraction of correctly
    retrieved sources.

    Args:
        retrieved_for_question: Retrieved sources for the question.
        truth_base_data: Ground-truth source locations.
        k: Number of retrieved sources to consider.
        minimal_for_pass: Minimum IoU required for a successful match.

    Returns:
        The Recall@k value for the question.
    """
    if len(truth_base_data) <= 0:
        return 1.0

    counter_founds: int = 0
    k_retrived: List[MinimalSource] = retrieved_for_question[:k]

    for t_obj in truth_base_data:
        for r_obj in k_retrived:
            if is_pass_after_calculate(r_obj, t_obj, minimal_for_pass) is True:
                counter_founds += 1
                break

    base_total: int = len(truth_base_data)
    return counter_founds / base_total


def calc_average(lst: List[float]) -> float:
    """
    Calculate the arithmetic mean of a list of values.

    Args:
        lst: List of floating-point values.

    Returns:
        The average of the values. Returns 0.0 if the list is empty.
    """
    if not lst:
        return 0.0
    return sum(lst) / len(lst)


def evaluate_search_results(questions_retrived_results: StudentSearchResults,
                            truth_dataset: RagDataset,
                            minimal_for_pass: float = 0.05
                            ) -> Dict[str, float]:
    """
    Evaluate retrieval performance on a dataset.

    The function compares the retrieved sources for each question with
    the corresponding ground-truth sources and computes Recall@1,
    Recall@3, Recall@5, and Recall@10.

    Args:
        questions_retrived_results: Retrieval results produced by the
            student system.
        truth_dataset: Dataset containing the reference answers and
            source locations.
        minimal_for_pass: Minimum IoU required for a retrieved source
            to be considered correct.

    Returns:
        A dictionary containing the number of evaluated questions and
        the Recall@1, Recall@3, Recall@5, and Recall@10 metrics.
    """
    qid_to_srcs: Dict[str, List[MinimalSource]] = {}
    counter: int = 0

    for obj in truth_dataset.rag_questions:
        if isinstance(obj, AnsweredQuestion):
            answerd_obj: AnsweredQuestion = obj
            qid_to_srcs.update(
                {answerd_obj.question_id: answerd_obj.sources}
                )

    recall_1: List = []
    recall_3: List = []
    recall_5: List = []
    recall_10: List = []

    for obj_minimal_search in questions_retrived_results.search_results:
        if obj_minimal_search.question_id not in qid_to_srcs:
            continue

        counter += 1
        stdnt_retvs: List[MinimalSource] = obj_minimal_search.retrieved_sources

        ground_truth: List[MinimalSource] | None = None
        ground_truth = qid_to_srcs[obj_minimal_search.question_id]

        recall_1.append(
            percent_in_k_retrives(
                stdnt_retvs,
                ground_truth,
                1, minimal_for_pass))

        recall_3.append(
            percent_in_k_retrives(stdnt_retvs,
                                  ground_truth,
                                  3, minimal_for_pass))

        recall_5.append(
            percent_in_k_retrives(stdnt_retvs,
                                  ground_truth,
                                  5, minimal_for_pass))

        recall_10.append(
            percent_in_k_retrives(stdnt_retvs,
                                  ground_truth,
                                  10, minimal_for_pass))

    return {
        "questions_evaluated": counter,
        "recall@1": calc_average(recall_1),
        "recall@3": calc_average(recall_3),
        "recall@5": calc_average(recall_5),
        "recall@10": calc_average(recall_10)
    }
