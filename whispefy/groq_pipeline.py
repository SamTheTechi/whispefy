from __future__ import annotations

import math
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .audio import RecordedAudio
from .config import TranscriptionConfig

SYSTEM_PROMPT = """
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

SIMILARITY_THRESHOLD = 0.8
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


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
        headers = {
            "Authorization": f"Bearer {self.api_key or os.getenv('GROQ_API_KEY', '')}"
        }
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

    def warmup_embedding_model(self) -> None:
        _get_embedding_model()

    def should_send_to_whisper(self, recording: RecordedAudio) -> bool:
        if recording.duration_seconds < 1.0:
            return False
        if recording.voiced_seconds < 0.25:
            return False
        min_peak = max(40.0, recording.noise_floor * 1.2)
        if recording.peak_rms < min_peak:
            return False
        return True

    def should_clean_transcript(self, transcript: str) -> bool:
        text = transcript.strip()
        if not text:
            return False

        words = [
            word.strip(".,!?;:")
            for word in text.split()
            if word.strip(".,!?;:")
        ]
        if len(words) < 3:
            return False

        if not any(
            len(word) >= 3 and any(ch.isalpha() for ch in word)
            for word in words
        ):
            return False
        return True

    def clean_transcript(self, transcript: str) -> str:
        if not self.should_clean_transcript(transcript):
            return transcript.strip()

        from langchain_core.messages import HumanMessage, SystemMessage
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
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=transcript.strip()),
            ]
        )
        cleaned = str(getattr(response, "content", response)).strip()
        if not cleaned:
            return transcript.strip()
        if not self.is_semantically_close(transcript, cleaned):
            return transcript.strip()
        return cleaned

    def is_semantically_close(self, original: str, cleaned: str) -> bool:
        embedding_model = _get_embedding_model()
        original_vec = embedding_model.embed_query(original.strip())
        cleaned_vec = embedding_model.embed_query(cleaned.strip())
        return _cosine_similarity(original_vec, cleaned_vec) >= SIMILARITY_THRESHOLD


@lru_cache(maxsize=1)
def _get_embedding_model():
    from langchain_community.embeddings import FastEmbedEmbeddings

    return FastEmbedEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
