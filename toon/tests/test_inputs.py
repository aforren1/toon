import unittest
import sys
from unittest import TestCase

from toon.input import DummyTime, Hand, BlamBirds, Keyboard, DebugKeyboard

#@unittest.skip("Have not figured out how to test external devices yet.")
class TestInputs(TestCase):
    def test_hand(self):
        dev = Hand()
        self.assertIsInstance(dev, Hand)
        with self.assertRaises(ValueError):
            dev = Hand(dims=(50, 14))

    def test_birds(self):
        with self.assertRaises(ValueError):
            dev = BlamBirds(ports=['COM5', 'COM6'], master='COM7', sample_ports=['COM7'])
        with self.assertRaises(ValueError):
            dev = BlamBirds(ports=['COM5', 'COM6'],
                            master='COM6',
                            sample_ports=['COM6'],
                            data_mode='quaternion')
        with self.assertRaises(ValueError):
            dev = BlamBirds(ports='COM2', master='COM2', sample_ports=['COM2'])
        with self.assertRaises(ValueError):
            dev = BlamBirds(ports=['a', 'b'], master=3, sample_ports=['a'])
        with self.assertRaises(ValueError):
            dev = BlamBirds(ports=['a', 'b'], master='a', sample_ports='a')
        with self.assertRaises(ValueError):
            dev = BlamBirds(ports=['a', 'b'], master='a', sample_ports=['c'])

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_ft(self):
        pass

    def test_keyboards(self):
        with self.assertRaises(ValueError):
            dev = Keyboard()
        with self.assertRaises(ValueError):
            dev = Keyboard(keys='a')
        with self.assertRaises(ValueError):
            dev = DebugKeyboard()
        with self.assertRaises(ValueError):
            dev = DebugKeyboard(keys='a')

