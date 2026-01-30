import os
import typer
from dotenv import load_dotenv
from src.runner import PipelineRunner
from src.logger import log

load_dotenv()
app = typer.Typer()


@app.command()
def fix(
        repo_name: str,
        issue_number: int,
        feedback: str = typer.Option("", "--feedback", "-f", help="Feedback from a previous review."),
):
    log.info("=" * 50)
    log.info("Coding Agent")
    log.info("=" * 50)

    runner = PipelineRunner(repo_name, issue_number)
    runner.run(feedback=feedback)


if __name__ == "__main__":
    app()
