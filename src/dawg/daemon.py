import logging
import time
from pathlib import Path

from dawg.brain.agent import Agent
from dawg.config.models import Config
from dawg.audio.stt import STT
from dawg.state.models import AppState, DaemonState
from dawg.audio.capture import AudioCapture
from dawg.audio.vad import VAD


logger = logging.getLogger(__name__)


class Daemon:
    def __init__(self, config: Config) -> None:
        self.state: AppState = AppState(config=config)

        self.audio: AudioCapture = AudioCapture()
        self.vad = VAD(sample_rate=self.audio.sample_rate)
        self.stt = STT()
        self.agent = Agent(
            "Be as concise and friendly as possible. avoid punctuation where unnecessary."
        )

        self._running = False
        self._silence_chunks_for_vad = 20
        self._listening_chunks: list = []
        logger.info("daemon initialized successfully")

    def start(self) -> None:
        self.state.config.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.state.config.memory_dir.mkdir(parents=True, exist_ok=True)
        self._running = True
        self._set_state(DaemonState.VAD)
        self.audio.start()
        logger.info("starting up daemon")
        self._run_loop()

    def stop(self) -> None:
        self._running = False
        self.audio.stop()
        self._set_state(DaemonState.STOPPED)
        logger.info("shutting down daemon")

    def start_listen(self) -> None:
        self._listening_chunks = []
        self._set_state(DaemonState.LISTENING)

    def stop_listen(self) -> None:
        chunk_count = len(self._listening_chunks)
        logger.info("listening stopped: chunk_count=%s", chunk_count)

        self._set_state(DaemonState.TRANSCRIBING)
        transcript = self.stt.transcribe_chunks(self._listening_chunks)
        logger.info("human: %r", transcript)

        reply = self.agent.respond(transcript)
        logger.info("dawg: %r", reply)

        self._listening_chunks = []
        self._set_state(DaemonState.VAD)

    def _set_state(self, next_state: DaemonState) -> None:
        if self.state.mode == next_state:
            return
        previous_state = self.state.mode
        self.state.mode = next_state
        logger.info("state change: %s -> %s", previous_state, next_state)

    def _run_loop(self) -> None:
        silent_chunk_count = 0

        while self._running:
            for chunk in self.audio.get_chunks():
                has_speech = self.vad.is_speech(chunk)

                # VAD branch
                if self.state.mode == DaemonState.VAD:
                    if has_speech:
                        silent_chunk_count = 0
                        self.start_listen()

                # LISTENING branch
                elif self.state.mode == DaemonState.LISTENING:
                    self._listening_chunks.append(chunk.copy())
                    if has_speech:
                        silent_chunk_count = 0
                    else:
                        silent_chunk_count += 1
                        if silent_chunk_count >= self._silence_chunks_for_vad:
                            self.stop_listen()
                            silent_chunk_count = 0

            time.sleep(0.01)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    config = Config(runtime_dir=Path("runtime"), memory_dir=Path("memory"))
    daemon = Daemon(config=config)
    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
