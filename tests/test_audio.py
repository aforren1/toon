from unittest import TestCase
from toon.audio import beep, beep_sequence


class TestAudio(TestCase):
    def test_beep(self):
        b1 = beep(440, 1, sample_rate=44100)
        self.assertEqual(len(b1), 44100)

    def test_beep_sequence(self):
        b3 = beep_sequence([440, 440, 500],
                           inter_click_interval=0.5,
                           dur_clicks=0.1)
        self.assertEqual(len(b3), 50715)
