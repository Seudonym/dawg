import json
import subprocess
from typing import Literal


def notify(
    title: str,
    message: str,
    type: Literal[
        "error",
        "success",
    ] = "success",
) -> str:
    payload = {"title": title, "body": message, "type": type, "duration": 5000}
    _ = subprocess.run(
        ["noctalia-shell", "ipc", "call", "toast", "send", json.dumps(payload)],
        capture_output=True,
        timeout=5,
    )
    return f"notification sent: {title}"
