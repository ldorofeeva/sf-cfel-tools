import time
from threading import Thread, Event

import numpy as np
import zmq

PORT = 60124
FLAGS = 0 | zmq.SNDMORE


class DaqStreamTester:
    def __init__(
            self,
            rate_s : int = 2,
    ):
        self.host = "*"
        self.rate_s = rate_s

        self.stopped = Event()

        zmq_context = zmq.Context()  # io_threads=4)
        self.poller = poller = zmq.Poller()

        # receive from backend:
        self.backend_socket = backend_socket = zmq_context.socket(zmq.SUB)
        self.backend_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        address = f"tcp://{self.host}:{PORT}"
        backend_socket.bind(address)

        poller.register(backend_socket, zmq.POLLIN)

        self.t0 = time.time()

    def has_data(self):
        events = dict(self.poller.poll(self.rate_s * 1000)) # check every 2 seconds in each worker
        return (self.backend_socket in events)

    def get_data(self):
        metadata = self.backend_socket.recv_json(FLAGS)
        image = self.backend_socket.recv(FLAGS, copy=False, track=False)
        image = np.frombuffer(image, dtype=metadata["type"]).reshape(metadata["shape"])
        return image, metadata

    def run(self):
        """
        Start broadcast in blocking way.
        """
        self._listen()

    def _listen(self):
        while not self.stopped.is_set():
            if not self.has_data():
                print(f"{time.time() - self.t0}: No data")
                continue

            raw_image, metadata = self.get_data()
            print(f"{time.time() - self.t0}")
            print(f"{metadata=}")
            print(f"Got Img {raw_image.shape=} min={np.min(raw_image)}, max={np.max(raw_image)}\n")

    def close(self):
        """Set closing flag and stop listener."""
        self.stopped.set()


if __name__ == "__main__":
    tester = DaqStreamTester()
    tester.run()
