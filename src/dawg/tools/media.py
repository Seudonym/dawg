import subprocess


def _mpris(action: str) -> str:
    _ = subprocess.run(
        ["playerctl", action],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return f"media: {action}"


def media_play() -> str:
    return _mpris("play")


def media_pause() -> str:
    return _mpris("pause")


def media_play_pause() -> str:
    return _mpris("play-pause")


def media_next() -> str:
    return _mpris("next")


def media_previous() -> str:
    return _mpris("previous")


def media_stop() -> str:
    return _mpris("stop")
