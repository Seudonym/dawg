import logging

import numpy as np
from faster_whisper import WhisperModel


logger = logging.getLogger(__name__)


class STT:
    def __init__(self) -> None:
        self.model = WhisperModel(
            model_size_or_path="small.en", device="cpu", compute_type="float32"
        )

    def transcribe_chunks(self, chunks: list[np.ndarray]) -> str:
        if not chunks:
            return ""

        audio_int16 = np.concatenate(chunks)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        segments, info = self.model.transcribe(audio_float32, language="en")
        text = " ".join(segment.text.strip() for segment in segments).strip()

        logger.info(
            "stt finished: duration=%.2fs language=%s text=%r",
            info.duration,
            info.language,
            text,
        )
        return text
