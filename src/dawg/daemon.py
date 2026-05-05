import logging
from dawg.config.models import Config
from dawg.state.models import AppState


class Daemon:
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self.state: AppState = AppState(config=config)

        self.logger: logging.Logger = logger
        self.logger.info("daemon initialized successfully")

    def start(self) -> None:
        self.logger.info("starting up daemon")
        pass

    def stop(self) -> None:
        self.logger.info("shutting down daemon")
        pass
