import re
from typing import List, Tuple
from .data_models import TextChunk
from json import dump
from ast import parse, get_source_segment, Expression

class MultiChunker:
    def __init__(self, paths, max_chunk = 2000):
        self.paths = paths
        self.chunks = {".txt": [], ".md": [], ".py": []}
        self.max_chunk = max_chunk

    def txt_md_chunker(
        self,
        mode = '.txt'
    ):
        for path in self.paths[mode]:
            with open(path) as f:
                raw_txt = f.read()
            if len(raw_txt) <= self.max_chunk:
                self.chunks[mode].append(
                    TextChunk(
                        text=raw_txt,
                        size=len(raw_txt),
                        chunk_type=mode,
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
                    self.chunks[mode].append(
                        TextChunk(
                            text=chunk_text,
                            size=len(chunk_text),
                            chunk_type=mode,
                            file_path=str(path),
                            first_character_index=start,
                            last_character_index=min(end, len(raw_txt)) - 1,
                        )
                    )
                    start = end
                    end += self.max_chunk
    def py_chunker(self) -> None:
        for path in self.paths['.py']:
            with open(path, encoding='utf-8') as f:
                code = f.read()

            tree = parse(code)
            body = tree.body
            search_from = 0

            for i, node in enumerate(body):
                node_text = get_source_segment(code, node) or ""
                node_start = code.find(node_text, search_from)
                node_end = node_start + len(node_text)
                search_from = node_end

                chunk_text, chunk_end = node_text, node_end

                if len(chunk_text) > self.max_chunk:
                    chunk_text = chunk_text[: self.max_chunk]
                    chunk_end = node_start + len(chunk_text)
                else:
                    for sibling in body[i + 1:]:
                        sibling_text = get_source_segment(code, sibling) or ""
                        remaining = self.max_chunk - len(chunk_text)
                        if len(sibling_text) > remaining:
                            break
                        sibling_start = code.find(sibling_text, chunk_end)
                        if sibling_start == -1:
                            break
                        chunk_text = code[node_start:sibling_start + len(sibling_text)]
                        chunk_end = sibling_start + len(sibling_text)

                self.chunks['.py'].append(
                    TextChunk(
                        text=chunk_text,
                        size=len(chunk_text),
                        chunk_type='.py',
                        file_path=str(path),
                        first_character_index=node_start,
                        last_character_index=chunk_end,
                    )
                )



    def start_chunker(self):
        # self.txt_md_chunker(mode='.md')
        # self.txt_md_chunker()
        self.py_chunker()
        return [self.chunks['.txt'], self.chunks['.md'], self.chunks['.py']]
