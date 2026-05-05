from dataclasses import dataclass

from dawg.config.models import Config


@dataclass
class AppState:
    config: Config
