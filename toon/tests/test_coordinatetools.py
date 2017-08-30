import numpy as np
from unittest import TestCase

from toon.toon.tools import cart2pol, pol2cart, cart2sph, sph2cart
from toon.toon.tools.coordinatetools import _shapend


class TestCoordinateTools(TestCase):
    def setUp(self):
        self.ex_2d = np.random.random((10, 2))
        self.ex_3d = np.random.random((10, 3))
        self.ex_1d = [1, 1, 1]

    def tearDown(self):
        pass

    def test_shape_helper(self):
        def shapend_shell2(*args):
            """Helper, otherwise I need to think about how *args get passed around"""
            a, b, c = _shapend(args, dims=2)
            return a, b, c
        def shapend_shell3(*args):
            """Helper, otherwise I need to think about how *args get passed around"""
            a, b, c = _shapend(args, dims=3)
            return a, b, c
        self.assertRaises(ValueError, shapend_shell2, (3, 3, 3))
        self.assertRaises(ValueError, shapend_shell3, self.ex_2d)
        self.assertRaises(ValueError, shapend_shell2, self.ex_3d)
        a1, b1, c1 = shapend_shell2(self.ex_2d)
        self.assertTupleEqual(self.ex_2d.shape, a1.shape)
        self.assertEqual(b1, True)
        self.assertEqual(c1, False)
        a2, b2, c2 = shapend_shell2(self.ex_2d.transpose())
        self.assertTupleEqual(self.ex_2d.shape, a2.shape)
        self.assertEqual(b2, True)
        self.assertEqual(c2, True)

    def test_2d_tools(self):
        # single elements
        self.assertTrue(np.isclose((2, 2), pol2cart(cart2pol(2, 2))).all())
        # lists (separate x,y)
        self.assertTrue(np.isclose((self.ex_1d, self.ex_1d), pol2cart(cart2pol(self.ex_1d, self.ex_1d))).all())
        # operating on n x 2, 2 x n arrays
        self.assertTrue(np.isclose(self.ex_2d, pol2cart(cart2pol(self.ex_2d))).all())
        self.assertTrue(np.isclose(self.ex_2d.transpose(), pol2cart(cart2pol(self.ex_2d.transpose()))).all())
        # lists of various dimensionality
        tmp = [[2, 2], [2, 2], [2, 2]]
        self.assertTrue(np.isclose(tmp, pol2cart(cart2pol(tmp))).all())
        tmp = [[2, 2, 2], [2, 2, 2]]
        self.assertTrue(np.isclose(tmp, pol2cart(cart2pol(tmp))).all())
        # non-zero reference
        self.assertTrue(np.isclose([4, 4], pol2cart(cart2pol([4, 4]))).all())
        self.assertTrue(np.isclose([4, 4], pol2cart(cart2pol([4, 4], ref=(1, 1)), ref=(1, 1))).all())
        # non-zero reference, arrays
        self.assertTrue(np.isclose(self.ex_2d, pol2cart(cart2pol(self.ex_2d, ref=(1, 1)), ref=(1, 1))).all())
        self.assertTrue(np.isclose(self.ex_2d.transpose(),
                                   pol2cart(cart2pol(self.ex_2d.transpose(), ref=(1, 1)), ref=(1, 1))).all())

    def test_3d_tools(self):
        self.assertTrue(np.isclose((2, 2, 2), sph2cart(cart2sph(2, 2, 2))).all())
        # operating on n x 3, 3 x n arrays
        self.assertTrue(np.isclose(self.ex_3d, sph2cart(cart2sph(self.ex_3d))).all())
        self.assertTrue(np.isclose(self.ex_3d.transpose(), sph2cart(cart2sph(self.ex_3d.transpose()))).all())
        # lists of various dimensionality
        tmp = [[2, 2], [2, 2], [2, 2]]
        self.assertTrue(np.isclose(tmp, sph2cart(cart2sph(tmp))).all())
        tmp = [[2, 2, 2], [2, 2, 2]]
        self.assertTrue(np.isclose(tmp, sph2cart(cart2sph(tmp))).all())
        # non-zero reference
        self.assertTrue(np.isclose([4, 4, 4], sph2cart(cart2sph([4, 4, 4]))).all())
        self.assertTrue(np.isclose([4, 4, 4], sph2cart(cart2sph([4, 4, 4], ref=(1, 1, 1)), ref=(1, 1, 1))).all())
        # non-zero reference, arrays
        self.assertTrue(np.isclose(self.ex_3d, sph2cart(cart2sph(self.ex_3d, ref=(1, 1, 1)), ref=(1, 1, 1))).all())
        self.assertTrue(np.isclose(self.ex_3d.transpose(),
                                   sph2cart(cart2sph(self.ex_3d.transpose(), ref=(1, 1, 1)), ref=(1, 1, 1))).all())
        # TODO: Look at 3x3 case (at least get the result to travel the pipeline successfully
