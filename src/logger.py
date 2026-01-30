from enum import IntEnum
from src.core.config import DEBUG


class LogLevel(IntEnum):
    QUIET = 0
    NORMAL = 1
    DEBUG = 2


class Logger:
    def __init__(self, level: LogLevel = None):
        if level is None:
            level = LogLevel.DEBUG if DEBUG else LogLevel.NORMAL
        self.level = level

    def agent(self, message: str):
        print(f"\n\033[1;32m Agent:\033[0m {message}")

    def tool_call(self, name: str, args: dict):
        if self.level >= LogLevel.NORMAL:
            args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in args.items())
            print(f"\033[33m   {name}\033[0m({args_str})")

    def tool_result(self, result: str):
        if self.level >= LogLevel.DEBUG:
            preview = result
            preview = preview.replace('\n', ' | ')
            print(f"\033[90m   -> {preview}\033[0m")

    def debug(self, message: str):
        if self.level >= LogLevel.DEBUG:
            print(f"\033[90m[debug] {message}\033[0m")

    def info(self, message: str):
        print(f"\033[36m{message}\033[0m")

    def error(self, message: str):
        print(f"\033[1;31m{message}\033[0m")

    def separator(self):
        print("\033[90m" + "-" * 50 + "\033[0m")


log = Logger()
