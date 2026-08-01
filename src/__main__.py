import fire
from json import dump
from pathlib import Path, PosixPath, PurePath
from .text_chunkers import MultiChunker
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


def scan(directory_path: str):
    extensions = {".txt"}
    paths = Path(directory_path).rglob("*")
    results = {'.txt': [], '.md': [],'.py': []}
    for file in paths:
        if file.is_file() and file.suffix == '.txt':
            results['.txt'].append(file)
        elif file.is_file() and file.suffix == '.md':
            results['.md'].append(file)
        elif file.is_file() and file.suffix == '.py':
            results['.py'].append(file)
             
    res = MultiChunker(results, 2000).start_chunker()
    for (path, r) in [('text.json', res[0]), ('markdown.json', res[1]), ('python.json', res[2])]:
        with open(path, "w") as file:
            dump([chunk.model_dump() for chunk in r], file, indent=2)


if __name__ == '__main__':
    fire.Fire()