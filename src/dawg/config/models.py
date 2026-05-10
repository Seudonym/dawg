from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    runtime_dir: Path
    memory_dir: Path
    system_prompt: Path
