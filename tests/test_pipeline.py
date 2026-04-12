import unittest
from pathlib import Path
from unittest.mock import patch

from whispefy.audio import RecordedAudio
from whispefy.config import TranscriptionConfig
from whispefy.groq_pipeline import GroqPipeline


class PipelineTests(unittest.TestCase):
    def test_should_send_to_whisper_gate(self):
        pipeline = GroqPipeline(
            api_key="test",
            transcription=TranscriptionConfig(
                model="whisper-large-v3-turbo",
                base_url="https://api.groq.com/openai/v1",
                timeout_seconds=60.0,
                name="groq-whisper-stt",
                language="en",
            ),
            llm_model="llama-3.1-8b-instant",
            llm_temperature=0.0,
        )

        self.assertFalse(
            pipeline.should_send_to_whisper(
                RecordedAudio(
                    wav_path=Path("/tmp/a.wav"),
                    duration_seconds=0.5,
                    voiced_seconds=0.2,
                    peak_rms=120.0,
                    noise_floor=40.0,
                )
            )
        )
        self.assertTrue(
            pipeline.should_send_to_whisper(
                RecordedAudio(
                    wav_path=Path("/tmp/a.wav"),
                    duration_seconds=1.4,
                    voiced_seconds=0.4,
                    peak_rms=130.0,
                    noise_floor=60.0,
                )
            )
        )

    def test_semantic_similarity_guardrail(self):
        pipeline = GroqPipeline(
            api_key="test",
            transcription=TranscriptionConfig(
                model="whisper-large-v3-turbo",
                base_url="https://api.groq.com/openai/v1",
                timeout_seconds=60.0,
                name="groq-whisper-stt",
                language="en",
            ),
            llm_model="llama-3.1-8b-instant",
            llm_temperature=0.0,
        )

        class DummyEmbeddingModel:
            def embed_query(self, text):
                if text == "hello world":
                    return [1.0, 0.0]
                if text == "hello, world":
                    return [0.98, 0.02]
                return [0.0, 1.0]

        with patch(
            "whispefy.groq_pipeline._get_embedding_model",
            return_value=DummyEmbeddingModel(),
        ):
            self.assertTrue(pipeline.is_semantically_close("hello world", "hello, world"))
            self.assertFalse(
                pipeline.is_semantically_close("hello world", "something else entirely")
            )

    def test_embedding_model_warmup(self):
        pipeline = GroqPipeline(
            api_key="test",
            transcription=TranscriptionConfig(
                model="whisper-large-v3-turbo",
                base_url="https://api.groq.com/openai/v1",
                timeout_seconds=60.0,
                name="groq-whisper-stt",
                language="en",
            ),
            llm_model="llama-3.1-8b-instant",
            llm_temperature=0.0,
        )

        with patch("whispefy.groq_pipeline._get_embedding_model") as get_model:
            pipeline.warmup_embedding_model()
            get_model.assert_called_once()


if __name__ == "__main__":
    unittest.main()
