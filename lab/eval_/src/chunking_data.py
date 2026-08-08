"""chunking data stratigies."""
from src.classes_types import Chunk
from typing import List, Any
import re
import ast
import os
from tqdm import tqdm


"""
Supported file extensions for code chunking.
"""
PYTHON_EXTENSIONS = {".py"}
TEXT_EXTENSIONS = {".md", ".txt"}

SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".o", ".a", ".lib", ".dll", ".exe",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
    ".zip", ".tar", ".gz", ".bz2", ".whl",
    ".bin", ".pt", ".pth", ".onnx", ".pb",
    ".lock", ".yaml", ".yml", ".toml"
}


def offset_lines_func(lines: List[str]) -> List[int]:
    """
    Calculate the starting character offset of each line.

    Args:
        lines: List of lines from a text file.

    Returns:
        A list containing the starting character offset for each line.
    """
    offsets: List = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line) + 1)
    return offsets


def split_large_chunk(file_path: str,
                      content: str,
                      start_offset: int,
                      max_chunk_size: int,
                      chunk_type: str) -> List[Chunk]:
    """
    Split a large chunk into smaller chunks.

    Args:
        file_path: Path to the source file.
        content: Content to split.
        start_offset: Starting character index within the file.
        max_chunk_size: Maximum size allowed for a chunk.
        chunk_type: Type of chunk being created.

    Returns:
        A list of Chunk objects that satisfy the size limit.
    """
    lines: List[str] = content.split("\n")
    chunk: str = ""
    offset: int = start_offset
    result: List = []

    for ln in lines:

        ln_with_newline: str = ln + "\n"
        if len(chunk) + len(ln_with_newline) <= max_chunk_size:
            chunk += ln_with_newline

        else:
            if chunk.strip():
                obj: Chunk = Chunk(
                    file_path=file_path,
                    content=chunk,
                    first_character_index=offset,
                    last_character_index=len(chunk) + offset,
                    chunk_type=chunk_type
                )
                result.append(obj)

            offset += len(chunk)
            chunk = ln_with_newline

    if chunk.strip():
        obj = Chunk(file_path=file_path,
                    content=chunk,
                    first_character_index=offset,
                    last_character_index=len(chunk) + offset,
                    chunk_type=chunk_type)
        result.append(obj)
    return result


def chunking_text_string_file(file_path: str,
                              content: str,
                              max_chunk_size: int = 2000) -> List[Chunk]:
    """
    Split a text document into chunks.

    Text files are split using markdown headings and paragraph
    boundaries when possible.

    Args:
        file_path: Path to the text file.
        content: File content.
        max_chunk_size: Maximum chunk size in characters.

    Returns:
        A list of generated text chunks.
    """
    result: List[Chunk] = []

    if len(content) <= max_chunk_size:
        if content.strip():
            obj: Chunk = Chunk(
                file_path=file_path,
                content=content,
                first_character_index=0,
                last_character_index=len(content),
                chunk_type="text"
            )
            result.append(obj)
        return result

    lst: List[str] = re.split(
        r"(?=^#{1,3} |\n\n)", content, flags=re.MULTILINE)

    chunk: str = ""
    start: int = 0

    for element in lst:
        if element == "":
            continue

        if len(chunk) + len(element) <= max_chunk_size:
            chunk += element

        else:
            if chunk.strip():
                obj = Chunk(
                    file_path=file_path,
                    content=chunk,
                    first_character_index=start,
                    last_character_index=start + len(chunk),
                    chunk_type="text"
                )
                result.append(obj)

            if len(element) > max_chunk_size:
                inner_chunks: List = split_large_chunk(
                    file_path,
                    element, start + len(chunk),
                    max_chunk_size, "text"
                )

                result.extend(inner_chunks)
                start = start + len(chunk) + len(element)
                chunk = ""

            else:
                start = start + len(chunk)
                chunk = element

    if chunk.strip():
        obj = Chunk(
            file_path=file_path,
            content=chunk,
            first_character_index=start,
            last_character_index=start + len(chunk),
            chunk_type="text"
        )
        result.append(obj)
    return result


def chunk_code_string_file(file_path: str,
                           content: str,
                           max_chunk_size: int = 2000) -> List[Chunk]:
    """
    Split a Python source file into chunks.

    The function extracts top-level classes and functions using
    Python's AST module. Large code blocks are further divided
    into smaller chunks.

    Args:
        file_path: Path to the source file.
        content: Python source code.
        max_chunk_size: Maximum chunk size in characters.

    Returns:
        A list of generated code chunks.
    """
    result: List[Chunk] = []

    try:

        tree: Any = ast.parse(content)

        top_level: List = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node,
                          (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
                          ):
                top_level.append(node)

        if not top_level:
            return chunking_text_string_file(file_path,
                                             content,
                                             max_chunk_size)

        lines: List[str] = content.split("\n")
        offsets: List[int] = offset_lines_func(lines)

        for node in top_level:
            start_line: int = int(node.lineno - 1)
            end_line: int = int(node.end_lineno)

            start_char: int = offsets[start_line]
            if end_line < len(offsets):
                end_char: int = offsets[end_line]
            else:
                end_char = len(content)

            node_content: str = (content[start_char:end_char])

            if len(node_content) > max_chunk_size:
                inner_chunks: List = split_large_chunk(
                    file_path,
                    node_content,
                    start_char,
                    max_chunk_size,
                    "python"
                )

                if len(inner_chunks) > 0:
                    result.extend(inner_chunks)
            else:
                obj: Chunk = Chunk(
                    file_path=file_path,
                    content=node_content,
                    first_character_index=start_char,
                    last_character_index=end_char,
                    chunk_type="python"
                )
                result.append(obj)

        if top_level:
            first_node_start_index: int = offsets[top_level[0].lineno - 1]
            if first_node_start_index > 0:
                above_data: str = content[:first_node_start_index].strip()
                if above_data:
                    above_chunks: List = split_large_chunk(
                        file_path,
                        above_data,
                        0,
                        max_chunk_size, "python"
                    )
                    result = above_chunks + result

    except Exception:
        return chunking_text_string_file(file_path, content, max_chunk_size)

    if not result:
        return chunking_text_string_file(file_path, content, max_chunk_size)

    return result


def chunk_repository(repo_path: str,
                     max_chunk_size: int = 2000) -> List[Chunk]:
    """
    Chunk all supported files within a repository.

    Python files are processed using AST-based chunking, while
    text files are processed using text chunking rules.

    Args:
        repo_path: Path to the repository.
        max_chunk_size: Maximum chunk size in characters.

    Returns:
        A list containing all generated chunks from the repository.
    """
    res_output: List[Chunk] = []
    all_files_path: List[str] = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            extention: Any = os.path.splitext(file)[1].lower()

            if extention in SKIP_EXTENSIONS:
                continue
            if (
                extention not in PYTHON_EXTENSIONS
                and extention not in TEXT_EXTENSIONS
            ):
                continue

            full_path_from_data_root: str = os.path.join(root, file)
            all_files_path.append(full_path_from_data_root)

    for the_path in tqdm(all_files_path, desc="Currently Chunking Progress"):
        try:
            with open(the_path, "r") as f:
                content_file_data: str = f.read()

            if not content_file_data.strip():
                continue

            extention = os.path.splitext(the_path)[1].lower()

            if extention in PYTHON_EXTENSIONS:
                res_chunks: List = chunk_code_string_file(
                    the_path,
                    content_file_data,
                    max_chunk_size
                )
                res_output.extend(res_chunks)

            elif extention in TEXT_EXTENSIONS:
                res_chunks = chunking_text_string_file(the_path,
                                                       content_file_data,
                                                       max_chunk_size)
                res_output.extend(res_chunks)

        except Exception as err:
            print(f"Error: While Process in Chunking Stage, Reason {err}")

    return res_output
