import numpy as np
from toon.tests.fake_class import FakeInput
from toon.input.base_input2 import MultiprocessInput
from time import sleep, time



single_data = FakeInput(data_dims = 5)

multi_data = FakeInput(data_dims=[5, [3, 2]])

single_mp = MultiprocessInput(device=single_data, nrow=20)

multi_mp = MultiprocessInput(device=multi_data, nrow=10)

with single_data as d:
    print(d.read())

with multi_data as d:
    print(d.read())

with single_mp as d:
    sleep(1)
    print(d.read())

with multi_mp as d:
    sleep(1)
    print(d.read())
