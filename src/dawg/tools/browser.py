import subprocess


def open_url(url: str) -> str:
    _ = subprocess.Popen(["xdg-open", url])
    return f"opened {url}"
