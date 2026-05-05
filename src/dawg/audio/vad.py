import numpy as np
import torch
from silero_vad import load_silero_vad


class VAD:
    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5) -> None:
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.model = load_silero_vad()

    def is_speech(self, chunk: np.ndarray) -> bool:
        audio_float32 = chunk.astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_float32)
        speech_prob = self.model(audio_tensor, self.sample_rate).item()
        return speech_prob >= self.threshold
