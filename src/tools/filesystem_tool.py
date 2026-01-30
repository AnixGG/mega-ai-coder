import os
import pathspec
from pathlib import Path
from langchain_core.tools import tool
from src.core.context import get_current_work_dir



class IgnoreManager:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.spec = self._load_ignore_spec()

    def _load_ignore_spec(self):
        ignores_patterns = ["__pycache__", "venv", ".git", ".gitignore"]
        coderignore_path = os.path.join(self.root_dir, ".coderignore")
        if os.path.exists(coderignore_path):
            with open(coderignore_path, "r") as f:
                ignores_patterns.extend(f.readlines())
        return pathspec.PathSpec.from_lines("gitwildmatch", ignores_patterns)

    def is_ignored(self, filepath: str) -> bool:
        rel_path = os.path.relpath(filepath, self.root_dir)
        return self.spec.match_file(rel_path)

@tool
def list_files(directory: str = "./"):
    """
    List all files in the repository, respecting .coderignore.
    Use this to understand the project structure.
    To understand the file structure, use `get_file_structure`.

    Args:
        directory: path to the root directory
    """

    try:
        root = Path(get_current_work_dir())
    except RuntimeError as e:
        return f"Error: {e}"

    target_dir = (root / directory).resolve()

    if not str(target_dir).startswith(str(root)):
        return f"Error: Access denied. Cannot list files outside of workspace: {target_dir}"

    if not target_dir.exists():
        return f"Error: Directory '{directory}' does not exist."

    manager = IgnoreManager(root)
    results = []

    for dirpath, _, filenames in os.walk(target_dir):
        if manager.is_ignored(dirpath):
            continue
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if not manager.is_ignored(full_path):
                results.append(os.path.relpath(full_path, root))
    return "\n".join(results[:1000])

