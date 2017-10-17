import multiprocessing as mp

class MultiprocessTest(object):
    def __init__(self):
        self.local, self.remote = mp.Pipe(duplex=False)
        # write to remote, read in local
        # oldest events read first

    def _mp_worker(self, remote):
        while True:
            x = {'data': 3, 'time': 2}
            remote.send(x)

    def read(self):
        data = list()
        while self.local.poll():
            data.append(self.local.recv())