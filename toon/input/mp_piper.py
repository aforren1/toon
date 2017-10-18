import multiprocessing as mp

class MultiprocessPiper(object):
    def __init__(self, device=None, _sampling_period=0):
        self._device = device
        self.local, self.remote = mp.Pipe(duplex=False)
        self.remote_ready = mp.Event()
        self.stop_remote = mp.Event()
        self._sampling_period = _sampling_period

    def __enter__(self):
        self._process = mp.Process(target=self._mp_worker,
                                   args=(self.remote,
                                         self.remote_ready,
                                         self.stop_remote))
        self._process.daemon = True
        self._clear_pipe()
        self._process.start()
        self.remote_ready.wait()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_remote.set()

    def _mp_worker(self, remote, remote_ready, stop_remote):
        with self._device as dev:
            remote_ready.set()
            while not stop_remote.is_set():
                t0 = dev.time()
                timestamp, data = dev.read()
                if timestamp is not None:
                    remote.send({'time': timestamp,
                                 'data': data})
                    while self._sampling_period > (dev.time() - t0):
                        pass

    def _clear_pipe(self):
        while self.local.poll():
            self.local.recv()

    def read(self):
        data = list()
        while self.local.poll():
            data.append(self.local.recv())
        if len(data) == 0:
            return None
        return data