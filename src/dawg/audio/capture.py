import threading
import queue
import logging
import pyaudio
import numpy as np
from collections.abc import Generator

logger = logging.getLogger(__name__)


class AudioCapture:
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate: int = sample_rate
        self.chunk_size: int = chunk_size
        self.pa: pyaudio.PyAudio = pyaudio.PyAudio()
        self.stream: pyaudio.Stream | None = None
        self.queue: queue.Queue[np.ndarray] = queue.Queue()
        self.is_recording: bool = False
        self._thread: threading.Thread | None = None

    def _record_loop(self) -> None:
        try:
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )
            logger.info("audio stream opened")

            while self.is_recording:
                try:
                    data = self.stream.read(
                        self.chunk_size, exception_on_overflow=False
                    )
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    self.queue.put(audio_array)
                except Exception as e:
                    logger.error(f"stream read error: {e}")
                    break

        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            logger.info("audio stream closed")

    def start(self) -> None:
        if self.is_recording:
            return

        self.is_recording = True

        while not self.queue.empty():
            _ = self.queue.get()

        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        logger.info("recording started")

    def stop(self) -> None:
        self.is_recording = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        logger.info("recording stopped")

    def get_chunks(self) -> Generator[np.ndarray, None, None]:
        while not self.queue.empty():
            yield self.queue.get()

    def __del__(self) -> None:
        self.pa.terminate()
