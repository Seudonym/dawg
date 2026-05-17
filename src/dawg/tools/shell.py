import subprocess
from typing import TypedDict


def list_files(directory: str) -> str:
    result = subprocess.run(["ls", "-F", directory], capture_output=True)
    files = result.stdout.decode("utf-8").split("\n")[:-1]
    return " ".join(files)
