import numpy as np
from unittest import TestCase

from toon.toon.tools import cart2pol, pol2cart

class TestCoordinateTools(TestCase):
    def setUp(self):
        self.ex_2d = np.random.random((10, 2))
        self.ex_3d = np.random.random((10, 3))

    def tearDown(self):
        pass

    def test_2d_tools(self):
        # single elements
        self.assertTrue(np.isclose((2,2), pol2cart(cart2pol(2,2))).all())

        # operating on n x 2, 2 x n arrays
        self.assertTrue(np.isclose(self.ex_2d, pol2cart(cart2pol(self.ex_2d))).all())
        self.assertTrue(np.isclose(self.ex_2d.transpose(), pol2cart(cart2pol(self.ex_2d.transpose()))).all())
        # lists of various dimensionality
        tmp = [[2,2], [2,2], [2,2]]
        self.assertTrue(np.isclose(tmp, pol2cart(cart2pol(tmp))).all())
        tmp = [[2,2,2], [2,2,2]]
        self.assertTrue(np.isclose(tmp, pol2cart(cart2pol(tmp))).all())
        # non-zero reference
        self.assertTrue(np.isclose([4,4], pol2cart(cart2pol([4,4]))).all())
        self.assertTrue(np.isclose([4,4], pol2cart(cart2pol([4,4], ref=(1,1)), ref=(1,1))).all())
        # non-zero reference, arrays
        self.assertTrue(np.isclose(self.ex_2d, pol2cart(cart2pol(self.ex_2d, ref=(1,1)), ref=(1,1))).all())
        self.assertTrue(np.isclose(self.ex_2d.transpose(),
                         pol2cart(cart2pol(self.ex_2d.transpose(), ref=(1,1)), ref=(1,1))).all())
