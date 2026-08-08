"""the generation stage."""
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.classes_types import MinimalSource
import torch
from typing import List, Any


MODEL: Any = None
TOKENIZER: Any = None
model_name: str = "Qwen/Qwen3-0.6B"


def loading_the_model() -> None:
    """
    Load the tokenizer and language model into memory.

    The model is loaded only once. If the tokenizer and model are
    already initialized, the function returns immediately.

    Returns:
        None.
    """
    global MODEL, TOKENIZER

    if MODEL is not None and TOKENIZER is not None:
        return

    print(f"\nSTART LOADING THE MODEL: {model_name}\n")

    TOKENIZER = AutoTokenizer.from_pretrained(
        model_name, trust_remote_code=True)

    MODEL = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
        device_map="auto",
        trust_remote_code=True
    )

    MODEL.eval()
    print("\nMODEL LOADED SUCCESSFULLY.\n")


def get_content_from_source_obj(src_obj: MinimalSource,
                                max_context_length: int = 2000) -> str:
    """
    Read the content referenced by a source object.

    The function extracts a text fragment from a file using the
    character indices stored in the source object. The extracted
    content is truncated if it exceeds the maximum context length.

    Args:
        src_obj: Source location describing the file and character
            range to read.
        max_context_length: Maximum number of characters to read.

    Returns:
        The extracted text. Returns an empty string if the content
        cannot be read.
    """
    try:
        with open(src_obj.file_path, "r") as file:
            file.seek(src_obj.first_character_index)
            length: int = (
                src_obj.last_character_index - src_obj.first_character_index)

            if length >= max_context_length:
                length = max_context_length

            string_text_content: str = file.read(length)

        return string_text_content
    except Exception:
        return ""


def generate_the_answer(
        user_question: str,
        sources: List[MinimalSource],
        max_context_length: int = 2000,
        max_new_tokens: int = 100
        ) -> str:
    """
    Generate an answer to a user question using retrieved sources.

    The function loads the language model if necessary, builds a
    prompt from the retrieved source contents, and generates an
    answer using the language model.

    Args:
        user_question: Question to answer.
        sources: Retrieved source locations used as context.
        max_context_length: Maximum number of characters read from
            each source.
        max_new_tokens: Maximum number of tokens to generate.

    Returns:
        The generated answer. If generation fails, an error message
        is returned instead.
    """
    loading_the_model()

    big_marge_context: str = ""
    i = 1
    for source_obj in sources:
        the_content: str = get_content_from_source_obj(
            source_obj,
            max_context_length
        )

        big_marge_context += "=" * 30
        big_marge_context += f"SOURCE: ({i})"
        big_marge_context += "=" * 30
        big_marge_context = big_marge_context + "\n" + the_content
        big_marge_context += "\n\n"
        i += 1

    fully_prompt = f"""

Sources:
{big_marge_context}
----------------------------------------------------------

answer on this question:
--> {user_question} <--
from the sources.


THE ANSWER:
    """

    try:
        inputs: Any = TOKENIZER(
            fully_prompt,
            return_tensors="pt"
        )

        outputs = MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.0,
            repetition_penalty=1.3
        )

        input_len: int = len(inputs["input_ids"][0].tolist())
        new_tokens: Any = outputs[0][input_len:]
        answer: str = TOKENIZER.decode(new_tokens, skip_special_tokens=True)

        return answer.strip()

    except Exception as e:
        return f"Error generating answer: {e}"
