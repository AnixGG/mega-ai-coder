import subprocess
import os
from langchain_core.tools import tool
from src.core.context import get_current_work_dir
from pathlib import Path


@tool
def run_tests(test_path: str = "."):
    """
    Run pytest to verify changes.
    Args:
        test_path: Path to a specific test file or directory (default is root).
    """

    try:
        root = Path(get_current_work_dir())
    except RuntimeError as e:
        return f"Error: {e}"

    config_files = ["pytest.ini", "pyproject.toml", "conftest.py", "tox.ini"]
    has_pytest_config = any((root / f).exists() for f in config_files)

    has_tests_dir = (root / "tests").exists()



    if not (has_pytest_config or has_tests_dir):
        return "Info: No tests detected in this repository. You MUST skip this step. Run end_tool."

    try:
        result = subprocess.run(
            ["pytest", test_path],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + "\n" + result.stderr

        if result.returncode == 0:
            return f"Tests Passed:\n{output[-500:]}"
        else:
            return f"Tests Failed:\n{output[-1000:]}\n\nHint: Analyze the failure and fix the code."

    except Exception as e:
        return f"Error running tests: {str(e)}"
