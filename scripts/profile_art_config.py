from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "profile-art.json"

@dataclass(frozen=True)
class RevealLoop:
    duration: float
    fade_start: float
    fade: float

    @classmethod
    def from_config(cls, values: dict[str, Any]) -> "RevealLoop":
        loop = cls(float(values["duration_seconds"]), float(values["fade_start_seconds"]), float(values["fade_seconds"]))
        if loop.fade_start + loop.fade >= loop.duration:
            raise ValueError("Reveal fade must finish before the loop restarts")
        return loop

    def opacity_key_times(self, delay: float, reveal_duration: float) -> tuple[float, float, float]:
        if delay + reveal_duration >= self.fade_start:
            raise ValueError("Reveal must finish before the fade starts")
        return (
            reveal_duration / self.duration,
            (self.fade_start - delay) / self.duration,
            (self.fade_start + self.fade - delay) / self.duration,
        )

def load_config(path: Path = DEFAULT_CONFIG, required: set[str] | None = None) -> dict[str, Any]:
    values = json.loads(path.read_text(encoding="utf-8"))
    missing = (required or set()).difference(values)
    if missing:
        raise ValueError(f"Missing profile art settings: {', '.join(sorted(missing))}")
    return values

def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path
