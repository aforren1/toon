import multiprocessing as mp
import ctypes

class MultiprocessTest(object):
    def __init__(self, device=None, _sampling_period=0):
        self._device = device
        self.local, self.remote = mp.Pipe(duplex=False)
        self.lock = mp.RLock()
        self.poison_pill = mp.Value(ctypes.c_bool)
        self._sampling_period = _sampling_period

        # write to remote, read in local
        # oldest events read first

    def __enter__(self):
        self.poison_pill.value = False
        self._process = mp.Process(target=self._mp_worker,
                                   args=(self.remote,
                                         self.lock,
                                         self.poison_pill))
        self._process.daemon = True
        self._clear_pipe()
        self._process.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.poison_pill.get_lock():
            self.poison_pill.value = True
        #self._process.join()

    def _mp_worker(self, remote, lock, poison_pill):
        with self._device as dev:
            stop_sampling = False
            while not stop_sampling:
                t0 = dev.time()
                with poison_pill.get_lock():
                    stop_sampling = poison_pill.value
                timestamp, data = dev.read()
                if timestamp is not None:
                    with lock:
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