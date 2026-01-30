import os
from pathlib import Path
from langchain_core.tools import tool
from src.core.context import get_current_work_dir


@tool
def replace_code_block(filepath: str, old_code: str, new_code: str):
    """
    Replace a specific block of code in a file.
    Args:
        filepath: path to file
        old_code: EXACT code block to be replaced (copy-paste from read_file)
        new_code: The new code to insert
    """

    base_path = Path(get_current_work_dir())
    full_path = (base_path / filepath).resolve()

    old_code = old_code.replace("\r\n", "\n")

    if not os.path.exists(full_path):
        return "Error: File not found."

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("\r\n", "\n")
    old_code = old_code.replace("\r\n", "\n")
    new_code = new_code.replace("\r\n", "\n")

    if old_code not in content:
        return "Error: Could not find the exact 'old_code' block in the file. Please ensure exact match."

    new_content = content.replace(old_code, new_code, 1)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return f"Successfully updated {filepath}"


@tool
def create_file(filepath: str, content: str) -> str:
    """
    Create a NEW file with the provided content.
    Use this only if the file does not exist yet.
    """
    base_path = Path(get_current_work_dir())
    full_path = (base_path / filepath).resolve()

    if os.path.exists(full_path):
        return f"Error: File {filepath} already exists. Use replace_code_block instead."

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Successfully created file {filepath}"
