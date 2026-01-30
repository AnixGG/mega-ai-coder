import os
from langchain_core.tools import tool

@tool
def end_tool():
    """
    Call this tool ONLY when the task is fully complete and all tests have passed.
    This signals that your work is done.

    Return DONE
    """
    return "Work finished. System will now terminate. Write ONLY `DONE`"