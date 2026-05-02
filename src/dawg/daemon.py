from dataclasses import dataclass
import logging
from pathlib import Path


@dataclass
class Config:
    runtime_dir: Path
    memory_dir: Path


@dataclass
class AppState:
    config: Config
    logger: logging.Logger


class Daemon:
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.state: AppState = AppState(config=config, logger=logger)
        self.state.logger.info("daemon initialized successfully")

    def start(self) -> None:
        self.state.logger.info("starting up daemon")
        pass

    def stop(self) -> None:
        self.state.logger.info("shutting down daemon")
        pass
