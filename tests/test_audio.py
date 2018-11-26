from toon.audio import beep, beep_sequence


def test_beep():
    b1 = beep(440, 1, sample_rate=44100)
    assert(len(b1) == 44100)


def test_beep_sequence():
    b3 = beep_sequence([440, 440, 500],
                       inter_click_interval=0.5,
                       dur_clicks=0.1)
    assert(len(b3) == 50715)
