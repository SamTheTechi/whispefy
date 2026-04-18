from __future__ import annotations

import logging
import signal
import threading

if __package__ in (None, ""):
    import pathlib
    import sys

    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
    from whispefy.audio import VoiceRecorder
    from whispefy.config import AppConfig
    from whispefy.groq_pipeline import GroqPipeline
    from whispefy.insertion import WaylandInserter
    from whispefy.notifications import notify
    from whispefy.server import build_server
else:
    from .audio import VoiceRecorder
    from .config import AppConfig
    from .groq_pipeline import GroqPipeline
    from .insertion import WaylandInserter
    from .notifications import notify
    from .server import build_server

logger = logging.getLogger(__name__)


class WhispefyApp:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._worker: threading.Thread | None = None
        self._server_thread: threading.Thread | None = None
        self._server = None
        self._shutdown = threading.Event()
        self._active = False
        self._lock = threading.Lock()

        self.recorder = VoiceRecorder(
            sample_rate=config.sample_rate,
            frame_ms=config.frame_ms,
            silence_ms=config.silence_ms,
        )
        self.pipeline = GroqPipeline(
            api_key=config.groq_api_key,
            transcription=config.transcription,
            llm_model=config.llm_model,
            llm_temperature=config.llm_temperature,
        )
        self.inserter = WaylandInserter()

    def start_background_server(self) -> None:
        if self._server_thread and self._server_thread.is_alive():
            return
        try:
            self._server = build_server(self.config.http_port, self)
        except OSError as exc:
            logger.exception(
                "Failed to bind HTTP server on port %s", self.config.http_port)
            raise RuntimeError(f"Failed to bind HTTP server on port {
                               self.config.http_port}") from exc
        self._server_thread = threading.Thread(
            target=self._server.run,
            daemon=True,
        )
        self._server_thread.start()

    def toggle(self) -> None:
        with self._lock:
            active = self._active
        self.stop() if active else self.start()

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._active

    def start(self) -> None:
        with self._lock:
            if self._active:
                return
            self._active = True

        self._worker = threading.Thread(target=self._run_session, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        notify("Whispefy: stopping...", self.config.notification_duration_ms)
        self.recorder.stop()

    def _run_session(self) -> None:
        try:
            notify("Whispefy Listening...")
            recording = self.recorder.record()
            if not self.pipeline.should_send_to_whisper(recording):
                print(
                    "[Whispefy] session cancelled: audio too short or too quiet",
                    flush=True,
                )
                return

            transcript = self.pipeline.transcribe(recording.wav_path).strip()
            if not transcript:
                raise RuntimeError("Groq returned an empty transcript")

            cleaned = self.pipeline.clean_transcript(transcript).strip()

            self.inserter.insert(cleaned or transcript)

        except Exception as err:
            logger.exception("Whispefy session failed")
            notify("Whispefy: session failed",
                   self.config.notification_duration_ms, urgency="critical")
        finally:
            with self._lock:
                self._active = False

    def shutdown(self) -> None:
        self._shutdown.set()
        self.recorder.stop()
        if self._server is not None:
            self._server.should_exit = True
            self._server.force_exit = True


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = AppConfig.from_env()
    app = WhispefyApp(config)
    try:
        print("[Whispefy] warming embedding model...", flush=True)
        app.pipeline.warmup_embedding_model()
    except Exception as exc:
        logger.warning("Embedding model warmup failed: %s", exc)
    try:
        app.start_background_server()
    except RuntimeError as exc:
        logger.error("%s", exc)

    def handle_signal(_signum, _frame):
        app.shutdown()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if app._server is not None:
        logger.info("Whispefy listening on http://127.0.0.1:%s",
                    config.http_port)
        print(
            f"[Whispefy] server on http://127.0.0.1:{config.http_port}", flush=True)

    try:
        while not app._shutdown.wait(0.5):
            pass
    finally:
        app.shutdown()
