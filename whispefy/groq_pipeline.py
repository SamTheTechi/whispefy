from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .config import TranscriptionConfig

SYSTEM_PROMPT = (
    """
    "You are a english expert who helps users clean up dictated text into perfect english"
        # Important Rules
        - Preserve the meaning exactly.
        - Fix punctuation, capitalization, spacing
        - Fix grammatical structure of given sentence and speech-recognition errors
        - Do not add commentary, headings or explanations
        - Output the *FINAL CLEANED TEXT ONLY*.
"""
)


@dataclass(slots=True)
class GroqPipeline:
    api_key: str | None
    transcription: TranscriptionConfig
    llm_model: str
    llm_temperature: float

    def _chat_base_url(self) -> str:
        base_url = self.transcription.base_url.rstrip("/")
        suffix = "/openai/v1"
        if base_url.endswith(suffix):
            return base_url[: -len(suffix)] or "https://api.groq.com"
        return base_url

    def transcribe(self, wav_path: Path) -> str:
        import httpx

        url = self.transcription.base_url.rstrip("/") + "/audio/transcriptions"
        headers = {"Authorization": f"Bearer {
            self.api_key or os.getenv('GROQ_API_KEY', '')}"}
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
            base_url=self._chat_base_url(),
            timeout=self.transcription.timeout_seconds,
            name=self.transcription.name,
        )
        response = model.invoke([("system", SYSTEM_PROMPT), ("human", transcript.strip())])
        content = getattr(response, "content", response)
        return str(content).strip()
