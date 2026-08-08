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
    def _node_boundaries(self, start: int, end: int) -> List[Tuple[int, int]]:
        """Split a [start, end) span into pieces, each at most max_chunk long.

        Args:
            start: Absolute character offset where the span begins.
            end: Absolute character offset where the span ends (exclusive).

        Returns:
            A list of (start, end) tuples covering the whole span, in order,
            with no gaps and no piece longer than max_chunk.
        """
        boundaries = []
        pos = start
        while pos < end:
            piece_end = min(pos + self.max_chunk, end)
            boundaries.append((pos, piece_end))
            pos = piece_end
        return boundaries

    def py_chunker(self) -> None:
        """Chunk every .py file in self.paths['.py'], appending to self.chunks['.py'].

        Each top-level node (function, class, statement) is located by its
        exact character offset in the source, then split in isolation via
        _node_boundaries. Nodes are never merged with their siblings, so
        every character in the file is covered by exactly one chunk.
        """
        for path in self.paths[".py"]:
            with open(path, encoding="utf-8") as f:
                code = f.read()

            tree = parse(code)
            search_from = 0

            for node in tree.body:
                node_text = get_source_segment(code, node) or ""
                if not node_text:
                    continue

                node_start = code.find(node_text, search_from)
                if node_start == -1:
                    continue
                node_end = node_start + len(node_text)
                search_from = node_end

                for start, end in self._node_boundaries(node_start, node_end):
                    self.chunks[".py"].append(
                        TextChunk(
                            text=code[start:end],
                            size=end - start,
                            chunk_type=".py",
                            file_path=str(path),
                            first_character_index=start,
                            last_character_index=end,
                        )
                    )



    def start_chunker(self):
        # self.txt_md_chunker(mode='.md')
        # self.txt_md_chunker()
        self.py_chunker()
        return [self.chunks['.txt'], self.chunks['.md'], self.chunks['.py']]
