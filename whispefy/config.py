from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return float(value)


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


@dataclass(slots=True)
class TranscriptionConfig:
    model: str
    base_url: str
    timeout_seconds: float
    name: str
    language: str


@dataclass(slots=True)
class AppConfig:
    groq_api_key: str | None
    http_port: int
    sample_rate: int
    frame_ms: int
    silence_ms: int
    transcription: TranscriptionConfig
    llm_model: str
    llm_temperature: float
    notification_duration_ms: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()
        return cls(
            groq_api_key=_env_str("GROQ_API_KEY", "") or None,
            http_port=_env_int("HTTP_PORT", 8765),
            sample_rate=_env_int("SAMPLE_RATE", 16000),
            frame_ms=_env_int("FRAME_MS", 20),
            silence_ms=_env_int("SILENCE_MS", 900),
            transcription=TranscriptionConfig(
                model=_env_str("TRANSCRIPTION_MODEL",
                               "whisper-large-v3-turbo"),
                base_url=_env_str(
                    "TRANSCRIPTION_BASE_URL", "https://api.groq.com/openai/v1"
                ),
                timeout_seconds=_env_float(
                    "TRANSCRIPTION_TIMEOUT_SECONDS", 60.0
                ),
                name=_env_str("TRANSCRIPTION_NAME", "groq-whisper-stt"),
                language=_env_str("LANGUAGE", "en"),
            ),
            llm_model=_env_str("LLM_MODEL", "llama-3.1-8b-instant"),
            llm_temperature=_env_float("LLM_TEMPERATURE", 0.0),
            notification_duration_ms=_env_int(
                "NOTIFICATION_DURATION_MS", 1600),
        )
