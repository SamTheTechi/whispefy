import unittest

from whispefy.audio import frame_samples, rms_level, silence_frame_count


class AudioTests(unittest.TestCase):
    def test_audio_helpers(self):
        self.assertEqual(frame_samples(16000, 20), 320)
        self.assertEqual(silence_frame_count(900, 20), 45)
        self.assertAlmostEqual(rms_level([0, 0, 0]), 0.0)
        self.assertGreater(rms_level([0, 10, 0, 10]), 0.0)


if __name__ == "__main__":
    unittest.main()
