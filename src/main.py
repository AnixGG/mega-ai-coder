import os
import sys
from dotenv import load_dotenv
from src.runner import PipelineRunner
from src.logger import log

load_dotenv()


def fix(repo_name: str, issue_number: int, feedback: str = ""):
    log.info("=" * 50)
    log.info("Coding Agent")
    log.info("=" * 50)

    runner = PipelineRunner(repo_name, issue_number)
    runner.run(feedback=feedback)


if __name__ == "__main__":
    while True:
        try:
            log.info("\nВведите данные (формат: repo_name issue_number [feedback])")
            log.info("Или 'exit' для выхода")
            user_input = input("> ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                log.info("Завершение работы")
                break

            if not user_input:
                continue

            parts = user_input.split(maxsplit=2)

            if len(parts) < 2:
                log.error("Ошибка: нужно указать repo_name и issue_number")
                continue

            repo_name = parts[0]

            try:
                issue_number = int(parts[1])
            except ValueError:
                log.error(f"Ошибка: issue_number должен быть числом, получено: {parts[1]}")
                continue

            feedback = parts[2] if len(parts) > 2 else ""

            fix(repo_name, issue_number, feedback)

        except KeyboardInterrupt:
            log.info("\nЗавершение работы")
            break
        except Exception as e:
            log.error(f"Критическая ошибка: {e}")
