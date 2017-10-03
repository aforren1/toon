from unittest import TestCase
from toon.audio import beep, beep_ramp, beep_sequence

class TestAudio(TestCase):
    def test_beep(self):
        b1 = beep(440, 1, sample_rate=44100)
        self.assertEqual(len(b1), 44100)

    def test_beep_ramp(self):
        b2 = beep_ramp(440, 1)
        self.assertEqual(len(b2), 44100)
    def test_beep_sequence(self):
        b3 = beep_sequence([440, 440, 500],
                           inter_click_interval=0.5,
                           num_clicks=3,
                           dur_clicks=0.1)
        self.assertEqual(len(b3), 68355)
        with self.assertRaises(ValueError):
            beep_sequence([330, 440], num_clicks = 100)
