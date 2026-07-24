import fire
from os import scandir

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
    file_paths = set()
    for entry in scandir(directory_path):
        if entry.is_file():
            file_paths.add(entry.path)

    print(file_paths[0].split)

if __name__ == '__main__':
    fire.Fire()