import re
from typing import List, Tuple
from .data_models import TextChunk
from json import dump

    # def py_chunker(self) -> List[TextChunk]:
    #     pass
    # def md_chunker(self) -> List[TextChunk]:
    #     pass
class TextChunker:
    def __init__(self, paths: List, max_chunk_size: int) -> None:
        self.paths = paths
        self.txt_chunked: List[TextChunk] = []
        self.max_chunk_size = max_chunk_size

    def _append_chunk(self, text: str, file_index: int, path: str, start: int) -> int:
        end = start + len(text)
        chunk = TextChunk(
            text=f"file {file_index} -->" + text,
            first_character_index=start,
            last_character_index=end,
            file_path=str(path),
            size=len(text),
        )
        self.txt_chunked.append(chunk)
        return end

    def _split_by_spaces(self, text: str, file_index: int, path: str, start: int) -> int:
        current_start = start
        current_chunk = ""

        for token in re.split(r"(\s+)", text):
            if not token:
                continue

            if len(token) > self.max_chunk_size:
                if current_chunk:
                    current_start = self._append_chunk(current_chunk, file_index, path, current_start)
                    current_chunk = ""

                while len(token) > self.max_chunk_size:
                    current_start = self._append_chunk(
                        token[: self.max_chunk_size], file_index, path, current_start
                    )
                    token = token[self.max_chunk_size :]

                current_chunk = token
                continue

            if len(current_chunk) + len(token) <= self.max_chunk_size:
                current_chunk += token
                continue

            if current_chunk:
                current_start = self._append_chunk(current_chunk, file_index, path, current_start)

            current_chunk = token

        if current_chunk:
            current_start = self._append_chunk(current_chunk, file_index, path, current_start)

        return current_start

    def _split_text(self, text: str, file_index: int, path: str, start: int) -> int:
        current_start = start
        current_chunk = ""

        for sentence in re.split(r"(?<=\.)", text):
            if not sentence:
                continue

            if len(sentence) > self.max_chunk_size:
                if current_chunk:
                    current_start = self._append_chunk(current_chunk, file_index, path, current_start)
                    current_chunk = ""

                current_start = self._split_by_spaces(sentence, file_index, path, current_start)
                continue

            if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                current_chunk += sentence
                continue

            if current_chunk:
                current_start = self._append_chunk(current_chunk, file_index, path, current_start)

            current_chunk = sentence

        if current_chunk:
            current_start = self._append_chunk(current_chunk, file_index, path, current_start)

        return current_start

    def txt_paragraphs(self) -> List[Tuple[str, int, int]]:
        indexes: List[Tuple[int, int]] = []
        for (i, path) in enumerate(self.paths):
            with open(path) as f:
                raw_text = f.read()
            start = 0
            for paragraph in raw_text.splitlines(keepends=True):
                previous_start = start
                start = self._split_text(paragraph, i, path, start)
                indexes.append((previous_start, start))
        with open('tests.json', 'w') as f:
            dump([chunk.model_dump() for chunk in self.txt_chunked], f, indent=2)
        return indexes
        

                
