import unittest


class ImportSmokeTests(unittest.TestCase):
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
