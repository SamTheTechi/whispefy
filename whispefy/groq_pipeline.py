from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .config import TranscriptionConfig

SYSTEM_PROMPT = (
    "You clean up dictated text for direct insertion into a desktop app. "
    "Preserve the meaning exactly. Fix punctuation, capitalization, spacing, "
    "and obvious speech-recognition errors. Do not add commentary, headings, "
    "or explanations. Output only the final cleaned text."
)


def _chat_base_url(base_url: str) -> str:
    return base_url.removesuffix("/openai/v1")


@dataclass(slots=True)
class GroqPipeline:
    api_key: str | None
    transcription: TranscriptionConfig
    llm_model: str
    llm_temperature: float

    def transcribe(self, wav_path: Path) -> str:
        import httpx

        url = self.transcription.base_url.rstrip("/") + "/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key or os.getenv('GROQ_API_KEY', '')}"}
        timeout = httpx.Timeout(self.transcription.timeout_seconds)
        with wav_path.open("rb") as handle:
            response = httpx.post(
                url,
                headers=headers,
                timeout=timeout,
                files={"file": (wav_path.name, handle, "audio/wav")},
                data={
                    "model": self.transcription.model,
                    "language": self.transcription.language,
                    "temperature": "0",
                    "response_format": "json",
                },
            )
        response.raise_for_status()
        data = response.json()
        return str(data.get("text", "")).strip()

    def clean_transcript(self, transcript: str) -> str:
        from langchain_groq import ChatGroq

        model = ChatGroq(
            model=self.llm_model,
            temperature=self.llm_temperature,
            api_key=self.api_key or os.getenv("GROQ_API_KEY"),
            base_url=_chat_base_url(self.transcription.base_url),
            timeout=self.transcription.timeout_seconds,
            name=self.transcription.name,
        )
        response = model.invoke([("system", SYSTEM_PROMPT), ("human", transcript.strip())])
        content = getattr(response, "content", response)
        return str(content).strip()
