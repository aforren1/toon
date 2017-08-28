# import numpy as np
# from unittest import TestCase
#
# from toon.tools import cart2pol, pol2cart
#
# class TestCoordinateTools(TestCase):
#     def setUp(self):
#         self.ex_2d = np.random.random((10, 2))
#         self.ex_3d = np.random.random((10, 3))
#
#     def tearDown(self):
#         pass
#
#     def test_2d_tools(self):
#         # single elements
#         # TODO
#         # operating on n x 2, 2 x n arrays
#         self.assertEqual(self.ex_2d, pol2cart(cart2pol(self.ex_2d)))
#         self.assertEqual(self.ex_2d.transpose(), pol2cart(cart2pol(self.ex_2d.transpose())))
#         # non-zero reference
#         self.assertEqual([4,4], pol2cart(cart2pol([4,4])))
#         self.assertEqual([3,3], pol2cart(cart2pol([4,4], ref=(1,1)), ref=(1,1)))
#         # non-zero reference, arrays
#         self.assertEqual(self.ex_2d, pol2cart(cart2pol(self.ex_2d, ref=(1,1)), ref=(1,1)))
#         self.assertEqual(self.ex_2d.transpose(),
#                          pol2cart(cart2pol(self.ex_2d.transpose(), ref=(1,1)), ref=(1,1)))
