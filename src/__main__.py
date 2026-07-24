import fire
from pathlib import Path, PosixPath, PurePath

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
    extensions = {".md", ".txt", ".py"}
    paths = Path(directory_path).rglob("*")
    for file in paths:
        if file.is_file() and file.suffix in extensions:
            # print(file)
            pass

if __name__ == '__main__':
    fire.Fire()