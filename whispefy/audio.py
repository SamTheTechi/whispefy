from __future__ import annotations

import logging
import queue
import threading
import wave
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RecordedAudio:
    wav_path: Path
    duration_seconds: float
    voiced_seconds: float
    peak_rms: float
    noise_floor: float


def frame_samples(sample_rate: int, frame_ms: int) -> int:
    return max(1, int(sample_rate * frame_ms / 1000))


def silence_frame_count(silence_ms: int, frame_ms: int) -> int:
    return max(1, int(silence_ms / frame_ms))


def rms_level(samples) -> float:
    import numpy as np

    values = np.asarray(samples, dtype=np.float32)
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(values))))


class VoiceRecorder:
    def __init__(
        self,
        sample_rate: int,
        frame_ms: int,
        silence_ms: int,
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.silence_ms = silence_ms
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def _frame_bytes(self, indata) -> bytes:
        import numpy as np

        return np.asarray(indata).reshape(-1).astype(np.int16, copy=False).tobytes()

    def _frame_rms(self, chunk: bytes) -> float:
        import numpy as np

        samples = np.frombuffer(chunk, dtype=np.int16)
        return rms_level(samples)

    def record(self) -> RecordedAudio:
        import sounddevice as sd

        frame_size = frame_samples(self.sample_rate, self.frame_ms)
        silence_frames = silence_frame_count(self.silence_ms, self.frame_ms)
        audio_frames: list[bytes] = []
        silence_run = 0
        speech_seen = False
        voiced_frames = 0
        peak_rms = 0.0
        noise_floor = 0.0
        speech_floor = 0.0
        frames: queue.Queue[bytes] = queue.Queue()
        speech_threshold_ratio = 1.4
        silence_threshold_ratio = 1.15

        def callback(indata, _frames, _time, status):
            if status:
                logger.warning("Audio status: %s", status)
            frames.put(self._frame_bytes(indata.copy()))

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=frame_size,
            callback=callback,
        ):
            while not self._stop_event.is_set():
                try:
                    chunk = frames.get(timeout=0.1)
                except queue.Empty:
                    continue

                if len(chunk) < frame_size * 2:
                    continue

                audio_frames.append(chunk)
                level = self._frame_rms(chunk)
                if not speech_seen:
                    noise_floor = level if noise_floor == 0.0 else noise_floor * 0.9 + level * 0.1
                    speech_threshold = noise_floor * speech_threshold_ratio
                    if level >= speech_threshold:
                        speech_seen = True
                        speech_floor = noise_floor
                        silence_run = 0
                else:
                    voiced_frames += 1
                    peak_rms = max(peak_rms, level)
                    noise_floor = noise_floor * 0.98 + level * 0.02
                    silence_threshold = noise_floor * silence_threshold_ratio
                    if level <= silence_threshold:
                        silence_run += 1
                    else:
                        silence_run = 0

                    if silence_run >= silence_frames:
                        break

        self._stop_event.clear()

        if not audio_frames:
            raise RuntimeError("No audio captured")
        wav_path = self._write_wav(audio_frames)
        duration_seconds = len(audio_frames) * self.frame_ms / 1000.0
        voiced_seconds = voiced_frames * self.frame_ms / 1000.0
        return RecordedAudio(
            wav_path=wav_path,
            duration_seconds=duration_seconds,
            voiced_seconds=voiced_seconds,
            peak_rms=peak_rms,
            noise_floor=speech_floor or noise_floor,
        )

    def _write_wav(self, frames: list[bytes]) -> Path:
        import tempfile

        audio = b"".join(frames)
        wav_path = Path(tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False).name)
        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio)
        return wav_path
