import os
import subprocess


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        _ = f.write(content)
    return f"wrote {len(content)} bytes to {path}"


def find_files(directory: str, keyword: str) -> str:
    result = subprocess.run(
        ["fd", "-atf", keyword, directory], capture_output=True
    ).stdout.decode("utf-8")
    return result
