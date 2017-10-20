import numpy as np
from toon.input.base_input import BaseInput
from numbers import Number

class FakeInput(BaseInput):
    def __init__(self, read_delay=0, **kwargs):
        self.data_dims = check_and_fix_dims(kwargs.pop('data_dims', 3))
        BaseInput.__init__(self, **kwargs)
        self.read_delay = read_delay
        self.t1 = 0  # first period will be wrong

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def read(self):
        t0 = self.time()
        data = list()
        for i in self.data_dims:
            data.append(np.random.random(i))
        while self.time() < self.t1:
            pass
        if len(data) == 1:
            data = data[0]
        self.t1 = self.time() + self.read_delay
        return {'time': self.time(), 'data': data}

def check_and_fix_dims(input):
    """
    Helper function to ensure data dimensions are consistent and unambiguous.
    Args:
        input: Scalar, list, or list of lists.
    Returns:
        List of lists.
    """
    # handle special-case, single scalar
    if isinstance(input, Number):
        input = [[input]]
    elif isinstance(input, (list, tuple, np.ndarray)):
        # special-case num 2, where we have a single scalar in a list
        if len(input) == 1 and isinstance(input[0], Number):
            input = [input]
        elif len(input) != 1 and any([isinstance(x, Number) for x in input]):
            raise ValueError('Ambiguous dimensions. There should be one list per expected piece of data' + \
                             ' from the input device.')
        # coerce array-like things to lists
        input = [list(x) for x in input]
        # now we're relatively comfortable we have a list of lists
    else:
        raise ValueError('Something is wrong with the input.')
    return input