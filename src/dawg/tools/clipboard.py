import subprocess


def clipboard_read() -> str:
    result = subprocess.run(
        ["wl-paste"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.stdout.strip() or "(empty)"


def clipboard_write(text: str) -> str:
    _ = subprocess.run(["wl-copy"], input=text, text=True, timeout=5)
    return f"copied {len(text)} chars to clipboard"
