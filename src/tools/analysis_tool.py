import os
from pathlib import Path
from langchain_core.tools import tool


from src.core.syntax_analyzer import SyntaxAnalyzer
from src.core.context import get_current_work_dir


@tool
def get_file_structure(filepath: str):
    """
    Analyzes the code structure using Tree-Sitter (AST).
    Returns a 'skeleton' of the file: classes, functions, and method signatures with line numbers.

    CRITICAL: Use this tool BEFORE `read_file` to save tokens. It helps you locate exactly which lines to read (e.g., "read lines 50-80").

    Args:
        filepath: Relative path to the file (e.g., "src/main.py")
    """
    base_path = Path(get_current_work_dir())
    full_path = (base_path / filepath).resolve()

    if not os.path.exists(full_path):
        return f"Error: File {filepath} does not exist."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return SyntaxAnalyzer.get_backbone(content, filepath)
    except UnicodeDecodeError:
        return "Error: Binary file detected. Cannot analyze structure."
    except Exception as e:
        return f"Error analyzing file: {e}"


@tool
def read_file(filepath: str, start_line: int = 1, end_line: int = -1):
    """
    Reads the content of a file, preferably a specific range of lines.

    CRITICAL: Reading entire files is expensive and inefficient.
    You SHOULD use this tool to read only small, relevant sections of code.
    First, use `get_file_structure` to find the line numbers of the function you need to inspect,
    then use this tool to read only that specific block.

    Example: If a function starts at line 50 and ends at line 75, call this as:
    `read_file(filepath="src/logic.py", start_line=50, end_line=75)`

    Args:
        filepath: Relative path to the file.
        start_line: (Optional) The line number to start reading from (1-based).
        end_line: (Optional) The line number to stop reading at. Defaults to the end of the file.
    """
    base_path = Path(get_current_work_dir())
    full_path = (base_path / filepath).resolve()

    if not os.path.exists(full_path):
        return f"Error: File {filepath} does not exist."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        start_idx = max(0, start_line - 1)

        if end_line == -1:
            end_idx = total_lines
        else:
            end_idx = min(end_line, total_lines)

        content = "".join(lines[start_idx:end_idx])

        return f"--- {filepath} (Lines {start_idx + 1}-{end_idx} of {total_lines}) ---\n{content}"

    except Exception as e:
        return f"Error reading file: {e}"
