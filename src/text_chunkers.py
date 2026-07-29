from typing import List
from .data_models import TextChunk

class TextChunker:
    def __init__(self, paths: List ) -> None:
        self.paths = paths
    def py_chunker(self) -> List[TextChunk]:
        pass
    def md_chunker(self) -> List[TextChunk]:
        pass
    def txt_chunker(self) -> List[TextChunk]:
        seps = ['\n', '. ', ' ']
        for path in self.paths:
            with open(path) as f:
                raw_text = f.read()
            
