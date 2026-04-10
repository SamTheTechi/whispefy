import unittest
from unittest.mock import patch

from whispefy.audio import frame_samples, silence_frame_count, rms_level
from whispefy.insertion import WaylandInserter
from whispefy.server import build_app


class PromptTests(unittest.TestCase):
    def test_audio_helpers(self):
        self.assertEqual(frame_samples(16000, 20), 320)
        self.assertEqual(silence_frame_count(900, 20), 45)
        self.assertAlmostEqual(rms_level([0, 0, 0]), 0.0)
        self.assertGreater(rms_level([0, 10, 0, 10]), 0.0)

    @patch("whispefy.insertion.subprocess.run")
    @patch("whispefy.insertion.shutil.which")
    def test_wayland_insert_paths(self, which, run):
        which.return_value = "/usr/bin/tool"
        WaylandInserter().insert("hello")
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args_list[0].args[0], ["wtype", "-"])

        run.reset_mock()
        run.side_effect = [RuntimeError("boom"), None, None]
        WaylandInserter().insert("hello")
        self.assertEqual(run.call_count, 3)
        self.assertEqual(
            run.call_args_list[1].args[0], ["wl-copy", "--type", "text/plain"]
        )
        self.assertEqual(
            run.call_args_list[2].args[0],
            ["wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"],
        )

    def test_fastapi_routes(self):
        from fastapi.testclient import TestClient

        class DummyApp:
            def __init__(self):
                self.active = False
                self.toggled = 0
                self.stopped = 0

            @property
            def is_active(self):
                return self.active

            def toggle(self):
                self.toggled += 1
                self.active = not self.active

            def stop(self):
                self.stopped += 1

        dummy = DummyApp()
        client = TestClient(build_app(dummy))
        self.assertEqual(client.get("/health").json(), {"status": "ok"})
        self.assertEqual(client.post("/toggle").json(),
                         {"ok": True, "active": True})
        self.assertEqual(client.post("/stop").json(), {"ok": True})
        self.assertEqual(dummy.toggled, 1)
        self.assertEqual(dummy.stopped, 1)

    def test_import_smoke(self):
        import whispefy
        import whispefy.app
        import whispefy.audio
        import whispefy.config
        import whispefy.groq_pipeline
        import whispefy.insertion
        import whispefy.notifications
        import whispefy.server

        self.assertTrue(hasattr(whispefy.app, "WhispefyApp"))
        self.assertTrue(hasattr(whispefy.audio, "VoiceRecorder"))
        self.assertTrue(hasattr(whispefy.config, "AppConfig"))
        self.assertTrue(hasattr(whispefy.groq_pipeline, "GroqPipeline"))
        self.assertTrue(hasattr(whispefy.insertion, "WaylandInserter"))
        self.assertTrue(hasattr(whispefy.notifications, "notify"))
        self.assertTrue(hasattr(whispefy.server, "build_app"))


if __name__ == "__main__":
    unittest.main()
