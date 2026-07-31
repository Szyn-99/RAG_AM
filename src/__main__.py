import fire
from pathlib import Path, PosixPath, PurePath
from .text_chunkers import TextChunker
def index(max_chunk_size: int):
    pass
def search(query, k: int):
    pass
def search_dataset(dataset_path: str, k:int, save_directory: str):
    pass
def answer(query, k: int):
    pass
def answer_dataset(student_search_results_path: str, save_directory: str):
    pass
def evaluate(student_search_results_path: str, dataset_path: str):
    pass


def scan(directory_path: str, to_save: str):
    extensions = {".txt"}
    paths = Path(directory_path).rglob("*")
    results = []
    for file in paths:
        if file.is_file() and file.suffix in extensions:
            results.append(file)
    tx = TextChunker(results, 2000)
    tx.txt_paragraphs()

if __name__ == '__main__':
    fire.Fire()