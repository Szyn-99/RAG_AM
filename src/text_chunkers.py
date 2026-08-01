import re
from typing import List, Tuple
from .data_models import TextChunk
from json import dump


class MultiChunker:
    def __init__(self, paths, max_chunk):
        self.avail_chunkers: List = []
        self.paths = paths
        self.chunks = {".txt": [], ".md": [], ".py": []}
        self.max_chunk = max_chunk

    def txt_chunker(
        self
    ):
        for path in self.paths:
            with open(path) as f:
                raw_txt = f.read()
            if len(raw_txt) <= self.max_chunk:
                self.chunks[".txt"].append(
                    TextChunk(
                        text=raw_txt,
                        size=len(raw_txt),
                        chunk_type=".txt",
                        file_path=str(path),
                        first_character_index=0,
                        last_character_index=len(raw_txt) - 1,
                    )
                )
            else:
                start = 0
                end = self.max_chunk

                while start < len(raw_txt):
                    chunk_text = raw_txt[start:end]
                    self.chunks['.txt'].append(
                        TextChunk(
                            text=chunk_text,
                            size=len(chunk_text),
                            chunk_type=".txt",
                            file_path=str(path),
                            first_character_index=start,
                            last_character_index=min(end, len(raw_txt)) - 1,
                        )
                    )
                    start = end
                    end += self.max_chunk
        return self.chunks['.txt']

