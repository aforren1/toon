# #from toon.input import Keyboard as kb
# from toon.input import Mouse as ms
# from time import time, sleep
#
# #dev = kb(multiprocess=True, keys = ['a', 's', 'd', 'f'])
# dev = ms(multiprocess=True)
#
# if __name__=='__main__':
#     with dev as d:
#         t0 = time()
#         t1 = t0 + 20
#         while time() < t1:
#             data, timestamp = d.read()
#             if data is not None:
#                 print((data, timestamp - t0))
#             sleep(0.016)
