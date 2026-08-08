import sys
import json
from typing import Any


def load_json(path: str) -> Any:
    """Load a JSON file and return its content."""
    try:
        with open(path, "r") as file:
            content = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
    return content


def calculat_overlap(start1: int, end1: int, start2: int, end2: int) -> int:
    """Calculate the overlap length between two character ranges."""
    overlap = min(end1, end2) - max(start1, start2)
    return overlap


def evaluation(
    student_search_results_path: str, dataset_path: str, k: int,
) -> float:
    """Calculate Recall@k by comparing retrieved
    sources with expected sources."""
    total = 0
    correct = 0

    student_datset = load_json(student_search_results_path)
    dataset = load_json(dataset_path)

    for data_student in student_datset["search_results"]:
        total += 1
        found = False

        for data in dataset["rag_questions"]:
            if data["question"] == data_student["question"]:
                for retrieve in data_student["retrieved_sources"]:
                    for source in data["sources"]:
                        if retrieve["file_path"] == source["file_path"]:
                            overlap = calculat_overlap(
                                retrieve["first_character_index"],
                                retrieve["last_character_index"],
                                source["first_character_index"],
                                source["last_character_index"],
                            )
                            if overlap > 0:
                                found = True
                                correct += 1
                                break
                    if found:
                        break

    recall = correct / total
    print(f"Recall@{k}: {recall:.3f} ({recall*100:.1f}%)")
    return recall
