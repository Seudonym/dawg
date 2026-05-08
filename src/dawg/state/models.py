from dataclasses import dataclass, field
from enum import StrEnum

from dawg.config.models import Config


class DaemonState(StrEnum):
    VAD = "vad"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    REPLYING = "replying"
    STOPPED = "stopped"


@dataclass
class AppState:
    config: Config
    mode: DaemonState = field(default=DaemonState.STOPPED)
