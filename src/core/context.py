import contextvars
from pathlib import Path

work_dir_context: contextvars.ContextVar[Path] = contextvars.ContextVar("workspace")

def get_current_work_dir() -> Path:
    try:
        return work_dir_context.get()
    except LookupError:
        raise RuntimeError("Work dir context is not set!")