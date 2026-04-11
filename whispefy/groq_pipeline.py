from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .config import TranscriptionConfig

SYSTEM_PROMPT = (
    """
    You are a speech-to-text cleanup engine.

    Your ONLY responsibility is to clean and format dictated text.
    You are NOT an assistant, chatbot, or knowledge source.

    STRICT RULES:
    - Do NOT answer questions
    - Do NOT explain anything
    - Do NOT add new information
    - Do NOT remove meaning
    - Do NOT summarize
    - Do NOT rewrite for style
    - Do NOT expand abbreviations unless obvious (e.g., "im" -> "I'm")
    - Do NOT interpret intent
    - Do NOT provide definitions

    ALLOWED CHANGES ONLY:
    - Fix grammar
    - Fix punctuation
    - Fix capitalization
    - Fix spacing
    - Fix obvious speech-recognition errors
    Break long sentences if needed

    BEHAVIOR CONSTRAINTS:
    - Preserve original wording as much as possible
    - If input is a question, keep it as a question
    - If input is incomplete, keep it incomplete
    - If input is short, keep it short
    - If input is nonsensical, keep it nonsensical but formatted

    IMPORTANT:
    - If the user asks a factual question, DO NOT answer it.
    - Only format the sentence.

    Examples:
    Input: what is cat
    Output: What is cat?

    Input: i going market tomorrow
    Output: I am going to the market tomorrow.

    Input: hello how are you
    Output: Hello, how are you?
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
        response = model.invoke(
            [("system", SYSTEM_PROMPT), ("human", transcript.strip())])
        content = getattr(response, "content", response)
        return str(content).strip()
