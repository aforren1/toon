from toon.util import priority


def test_priority():
    for i in range(3):
        assert(priority(i) is not None)
