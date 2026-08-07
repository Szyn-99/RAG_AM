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
    def py_chunker(self):
        def absolute_index(line_starts, line, col):
            return line_starts[line - 1] + col

        def next_node(tree, node, x):
            body = tree.body
            i = body.index(node)

            if i + x < len(body):
                return body[i + x]

            return None

        for path in self.paths['.py']:
            with open(path) as py:
                code = py.read()
            line_starts = [0]
            for line in code.splitlines(keepends=True):
                line_starts.append(line_starts[-1] + len(line))
            tree = parse(code)
            for n in tree.body:
                t = get_source_segment(code, n) or ""
                x = 1
                last_valid = n
                if len(t) > self.max_chunk:
                    t = t[:self.max_chunk]

                while len(t) < self.max_chunk:
                    nn = next_node(tree, n, x)
                    if not nn:
                        break

                    segment = get_source_segment(code, nn)
                    if segment is None:
                        break

                    remaining = self.max_chunk - len(t)
                    if len(segment) > remaining:
                        break

                    t += segment
                    last_valid = nn
                    x += 1

                self.chunks['.py'].append(
                    TextChunk(
                        text=t,
                        size=len(t),
                        chunk_type='.py',
                        file_path=str(path),
                        first_character_index=absolute_index(line_starts, n.lineno, n.col_offset),
                        last_character_index=absolute_index(line_starts, last_valid.end_lineno, last_valid.end_col_offset) - 1,
                    )
                )



    def start_chunker(self):
        # self.txt_md_chunker(mode='.md')
        # self.txt_md_chunker()
        self.py_chunker()
        return [self.chunks['.txt'], self.chunks['.md'], self.chunks['.py']]
