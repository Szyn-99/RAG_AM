"""the main start point."""
from src.indexing_and_retrieval import (build_the_indexed_stock,
                                        load_indexed_data_from_disk,
                                        retrieval)

import os
import sys
import fire
import json
from src.classes_types import (RagDataset,
                               MinimalSearchResults,
                               StudentSearchResults,
                               MinimalAnswer,
                               StudentSearchResultsAndAnswer,
                               Chunk,
                               MinimalSource)

from tqdm import tqdm
from src.the_generation import generate_the_answer
from src.evaluation import evaluate_search_results
from typing import Any, List, Dict, Optional


class RAGCliClass:
    """
    Command-line interface for the RAG system.

    Provides commands for indexing repositories, retrieving relevant
    source code, generating answers, and evaluating retrieval results.
    """

    def index(self, base_repo: str = "data/raw/vllm-0.10.1",
              max_chunk_size: int = 2000) -> None:
        """
        Build the BM25 index for a repository.

        Args:
            base_repo: Path to the repository to index.
            max_chunk_size: Maximum number of characters per chunk.

        Returns:
            None.
        """
        if not os.path.exists(base_repo):
            print(f"The Repo Base Path: {base_repo}, Does not Exists.\n")
            sys.exit(1)
        build_the_indexed_stock(base_repo, max_chunk_size)

    def search(self, query: str, k: int = 10) -> None:
        """
        Retrieve and display the top-k relevant source chunks.

        Args:
            query: User search query.
            k: Number of results to retrieve.

        Returns:
            None.
        """
        if k == 0:
            print("Please Enter k > 0")
            sys.exit(1)
        if not query or not query.strip():
            print("Error, There is no QUESTION, Enter one.")
            sys.exit(1)

        try:
            bm25_pack_obj: Any = None
            chunks_list_obj: List[Chunk] = []
            bm25_pack_obj, chunks_list_obj = load_indexed_data_from_disk()
        except Exception as err:
            print(f"Error, {err}")
            sys.exit(1)
        retrvd_lst_obj: List[MinimalSource] = retrieval(query,
                                                        bm25_pack_obj,
                                                        chunks_list_obj, k)

        print(f"\nTOP {k} RETRIEVED RESULTS FOR THE QUESTION -> '{query}'\n")
        i = 0
        while (i < len(retrvd_lst_obj)):
            print(f"{i + 1}. {retrvd_lst_obj[i].file_path}", end="")
            print(f"[{retrvd_lst_obj[i].first_character_index}", end="")
            print(f":{retrvd_lst_obj[i].last_character_index}]")
            i += 1

    def search_dataset(self, dataset_path: str,
                       k: int = 10,
                       save_directory: str = "data/output/search_results"
                       ) -> None:
        """
        Retrieve relevant sources for every question in a dataset.

        The generated retrieval results are saved as a JSON file.

        Args:
            dataset_path: Path to the dataset containing the questions.
            k: Number of retrieved sources for each question.
            save_directory: Directory where the results will be stored.

        Returns:
            None.
        """
        if k == 0:
            print("Please Enter k > 0")
            sys.exit(1)

        if not os.path.exists(dataset_path):
            print("Error, Dataset path does not exist.")
            sys.exit(1)

        try:
            bm25_pack_obj: Any = None
            chunks_list_obj: List[Chunk] = []
            bm25_pack_obj, chunks_list_obj = load_indexed_data_from_disk()
        except Exception as err:
            print(f"Error, {err}")
            sys.exit(1)

        try:
            with open(dataset_path, "r") as file:
                as_string: str = file.read()
                dcty: Dict = json.loads(as_string)
            rgdataset_obj: RagDataset = RagDataset(**dcty)
        except Exception as err:
            print(f"Error, while loading a dataset {err}")
            sys.exit(1)

        search_results: List[MinimalSearchResults] = []
        for unanswerd_obj in tqdm(rgdataset_obj.rag_questions,
                                  desc="(Retrieving srcs for QUESTIONS)"):

            srcs_current_question_retvd: List[MinimalSource] = retrieval(
                unanswerd_obj.question,
                bm25_pack_obj,
                chunks_list_obj, k)

            search_obj: MinimalSearchResults = MinimalSearchResults(
                question_id=unanswerd_obj.question_id,
                question=unanswerd_obj.question,
                retrieved_sources=srcs_current_question_retvd)

            search_results.append(search_obj)

        sdt_search_res: StudentSearchResults = StudentSearchResults(
            search_results=search_results, k=k)

        os.makedirs(save_directory, exist_ok=True)

        filename: Any = os.path.basename(dataset_path)
        save_full_path: str = os.path.join(save_directory, filename)

        with open(save_full_path, "w") as file:
            as_string = sdt_search_res.model_dump_json(indent=2)
            file.write(as_string)

        print(f"\n'RETRIEVED DATA' ARE SAVED IN: {save_full_path} PATH.")

    def answer(self, query: str, k: int = 10) -> None:
        """
        Generate an answer for a user question.

        The method retrieves the top-k relevant sources and passes them
        to the language model to generate an answer.

        Args:
            query: User question.
            k: Number of retrieved sources.

        Returns:
            None.
        """
        if k == 0:
            print("Please Enter k > 0")
            sys.exit(1)

        if not query or not query.strip():
            print("\nError, THERE IS NO QUESTION ENTER ONE.\n")
            sys.exit(1)

        try:
            bm25_obj: Any = None
            chunks_list: List[Chunk] = []
            bm25_obj, chunks_list = load_indexed_data_from_disk()
        except Exception as err:
            print(f"Error, {err}")
            sys.exit(1)

        sources_obj: List[MinimalSource] = retrieval(
            query, bm25_obj, chunks_list, k)

        print(f"\nWE RETRIEVED {len(sources_obj)}", end="")
        print("sources. BASE ON THEM WILL GENERATE AN ANSWER.....\n")

        print("SOURCES:")
        print("=" * 100)
        for src in sources_obj:
            print(f"  - {src.file_path} [{src.first_character_index}:", end="")
            print(f"{src.last_character_index}]")

        print("=" * 100)
        the_answer: str = generate_the_answer(query, sources_obj)
        print("\n\n")
        print(f"THE ANSWER IS:\n* {the_answer}\n")

    def answer_dataset(
            self,
            student_search_results_path: str,
            save_directory: str = "data/output/search_results_and_answer",
            max_new_tokens: int = 100) -> None:
        """
        Generate answers for every question in a retrieval results file.

        The generated answers are saved as a JSON file.

        Args:
            student_search_results_path: Path to the retrieval results.
            save_directory: Directory where the generated answers are saved.
            max_new_tokens: Maximum number of tokens generated for each answer.

        Returns:
            None.
        """
        if not os.path.exists(student_search_results_path):
            print("Error, Student search results 'PATH' does not exist.")
            sys.exit(1)

        try:
            with open(student_search_results_path, "r") as file:
                as_string: str = file.read()
                full_dict_obj: Dict = json.loads(as_string)
            search_results_obj: StudentSearchResults = StudentSearchResults(
                **full_dict_obj
            )

        except Exception as err:
            print(f"Error, {err}")
            sys.exit(1)
        print(f"\nLOADED {len(search_results_obj.search_results)}", end="")
        print(f"QUESTION WITH SOURCES, from: {student_search_results_path}.")

        answeres_objs: List = []
        i = 1

        for min_search_res_obj in tqdm(search_results_obj.search_results,
                                       desc="Generating For All Questions"):

            the_asnwer: str = generate_the_answer(
                min_search_res_obj.question,
                min_search_res_obj.retrieved_sources,
                max_new_tokens=max_new_tokens)

            min_answer_obj: MinimalAnswer = MinimalAnswer(
                question_id=min_search_res_obj.question_id,
                question=min_search_res_obj.question,
                retrieved_sources=min_search_res_obj.retrieved_sources,
                answer=the_asnwer)

            answeres_objs.append(min_answer_obj)
            print(f"\nProcessed {i}/{len(search_results_obj.search_results)}")
            i += 1

        searchs_and_answers_obj: Optional[StudentSearchResultsAndAnswer] = None
        searchs_and_answers_obj = StudentSearchResultsAndAnswer(
            search_results=answeres_objs, k=search_results_obj.k)

        os.makedirs(save_directory, exist_ok=True)
        filename: Any = os.path.basename(student_search_results_path)
        save_path: str = os.path.join(save_directory, filename)

        with open(save_path, "w") as f:
            as_string = searchs_and_answers_obj.model_dump_json(indent=2)
            f.write(as_string)

        print(f"\nSaved student_search_results_and_answer to: {save_path}\n")

    def evaluate(
            self,
            student_results_path: str,
            dataset_path: str,
            min_for_pass: float = 0.05) -> None:
        """
        Evaluate retrieval performance against the reference dataset.

        Recall@1, Recall@3, Recall@5, and Recall@10 are calculated and
        displayed.

        Args:
            student_results_path: Path to the student's retrieval results.
            dataset_path: Path to the reference dataset.
            min_for_pass: Minimum IoU threshold required for a retrieved
                source to be considered correct.

        Returns:
            None.
        """
        if not os.path.exists(student_results_path):
            print("Error, Student Result Path does not exist.")
            sys.exit(1)

        if not os.path.exists(dataset_path):
            print("Error,Base DataSet Path does not exist.")
            sys.exit(1)

        try:
            with open(student_results_path, "r") as file:
                as_string: str = file.read()
                full_dict: Dict = json.loads(as_string)
            student_res_obj: StudentSearchResults = StudentSearchResults(
                **full_dict)

        except Exception as err:
            print(f"Error, Loading Student Search results {err}")
            sys.exit(1)

        try:
            with open(dataset_path, "r") as file:
                as_string = file.read()
                fully_dict: Dict = json.loads(as_string)
            truth_dataset_obj: RagDataset = RagDataset(**fully_dict)
        except Exception as err:
            print(f"Error, While Loading Dataset {err}")
            sys.exit(1)

        dct_res: Dict = evaluate_search_results(
            student_res_obj, truth_dataset_obj, min_for_pass)

        print("\nEvaluation Results")
        print("=" * 40)
        print("Questions evaluated: %d" % dct_res["questions_evaluated"])

        print("Recall@1:  %.3f (%.1f%%)" %
              (dct_res["recall@1"], dct_res["recall@1"] * 100))

        print("Recall@3:  %.3f (%.1f%%)" %
              (dct_res["recall@3"], dct_res["recall@3"] * 100))

        print("Recall@5:  %.3f (%.1f%%)" %
              (dct_res["recall@5"], dct_res["recall@5"] * 100))

        print("Recall@10: %.3f (%.1f%%)" %
              (dct_res["recall@10"], dct_res["recall@10"] * 100))

        dct_res.pop("questions_evaluated")
        print(dct_res)


if __name__ == "__main__":
    try:
        fire.Fire(RAGCliClass)
    except Exception as err:
        print(err)
