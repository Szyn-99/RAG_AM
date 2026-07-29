from typing import List, Tuple
from .data_models import TextChunk



    # def py_chunker(self) -> List[TextChunk]:
    #     pass
    # def md_chunker(self) -> List[TextChunk]:
    #     pass
class TextChunker:
    def __init__(self, paths: List, max_chunk_size: int) -> None:
        self.paths = paths
        self.txt_chunked: List[TextChunk] = []
        self.max_chunk_size = max_chunk_size
    def txt_paragraphs(self) -> List[Tuple[str, int, int]]:
        seps = ['\n', '. ', ' ']
        