from typing import List
from .data_models import TextChunk



    # def py_chunker(self) -> List[TextChunk]:
    #     pass
    # def md_chunker(self) -> List[TextChunk]:
    #     pass
class TextChunker:
    def __init__(self, paths: List, max_chunk_size: int) -> None:
        self.paths = paths
        self.txt_chunked: List[TextChunk] = []
        self.mcs = max_chunk_size
    def txt_chunker(self) -> List[TextChunk]:
        seps = ['\n', '. ', ' ']
        def first_step(self, raw_text: str) -> list[str]:
            chunks = raw_text.split('\n')
            for chunk in chunks:
                if len(chunk) >= self.mcs:
                    

        for path in self.paths:
            with open(path) as f:
                raw_text = f.read()
