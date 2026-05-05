import logging
from dawg.config.models import Config
from dawg.state.models import AppState
from dawg.audio.capture import AudioCapture


logger = logging.getLogger(__name__)


class Daemon:
    def __init__(self, config: Config) -> None:
        self.state: AppState = AppState(config=config)
        self.audio: AudioCapture = AudioCapture()
        logger.info("daemon initialized successfully")

    def start(self) -> None:
        logger.info("starting up daemon")

    def stop(self) -> None:
        logger.info("shutting down daemon")

    def start_listen(self) -> None:
        logger.info("triggering audio capture start")
        self.audio.start()

    def stop_listen(self) -> None:
        logger.info("triggering audio capture stop")
        self.audio.stop()
