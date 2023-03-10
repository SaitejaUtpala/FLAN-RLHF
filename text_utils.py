from typing import List, Tuple, Optional
from transformers import AutoTokenizer
from datasets import Dataset


def split_into_last_prompt_and_last_output(
    dialogs: List[str],
) -> Tuple[List[str], List[str]]:
    last_prompts: List[str] = []
    last_outputs: List[str] = []

    delim = "Assistant: "
    for dialog in dialogs:
        head, sep, tail = dialog.rpartition(delim)
        last_prompt = head + sep
        last_output = tail
        last_prompts.append(last_prompt)
        last_outputs.append(last_output)

    return last_prompts, last_outputs


def tokenized_dataset(
    dataset: Dataset,
    num_proc:Optional[int]=2,
    col: Optional[str] = "chosen",
    model: Optional[str] = "google/flan-t5-small",
) -> Dataset:
    def tokenize(data):
        last_prompts, last_outputs = split_into_last_prompt_and_last_output(
            data[col]
        )
        return tokenizer(last_prompts, last_outputs, truncation=True)

    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
    tokenized_dataset = dataset.map(tokenize, batched=True, num_proc = num_proc)
    return tokenized_dataset


def test_split_into_last_prompt_and_last_output():
    dialogs = [
        "Human: str1 Assistant: str2",
        "Human: str1 Assistant: str2 Human: str3 Assistant: str4",
    ]
    expected_last_prompts = [
        "Human: str1 Assistant: ",
        "Human: str1 Assistant: str2 Human: str3 Assistant: ",
    ]
    expected_last_outputs = ["str2", "str4"]
    last_prompts, last_outputs = split_into_last_prompt_and_last_output(dialogs)
    assert expected_last_prompts == last_prompts
    assert expected_last_outputs == last_outputs
