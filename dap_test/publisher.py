import sys
import time
from threading import Event

import numpy as np
import zmq
from h5py import File

FLAGS = 0


class DaqStreamEmulator:
    PORT = 60123
    HOST = "*"

    def __init__(
            self,
            data_file: str,
            rate_s: int,
            socket_type: int = zmq.PUSH
    ):
        self.rate_s = rate_s
        self.stopped = Event()

        zmq_context = zmq.Context()  # io_threads=4)
        self.pub_sock = zmq_context.socket(socket_type=socket_type)
        address = f"tcp://{self.HOST}:{self.PORT}"
        self.pub_sock.bind(address)

        self.data = None
        self.data_file = data_file
        self.md = {
            "shape": (2, 2),  # Empty frame
            "is_good_frame": True,
            "pedestal_file": "/sf/jungfrau/data/pedestal/JF07T32V01/20230414_100746.h5",  # "/sf/bernina/exp/example_data/Ge_tt/pedestal_20190304_0545.JF07T32V01.res.h5",
            "detector_name": "JF07T32V01",
            "gain_file": "/sf/jungfrau/config/gainMaps/JF07T32V01/gains.h5"
        }
        self.iter = 0

    def load_data(self):
        if self.data_file.endswith(".h5"):
            with File(self.data_file, "r") as df:
                self.data = np.asarray(df["data/data"])
        elif self.data_file.endswith(".npy"):
            self.data = np.load(self.data_file)

    def _gen_data_frame(self):
        idx = self.iter % self.data.shape[0]
        im = np.ascontiguousarray(self.data[idx])
        return im

    def run(self, blocking=True):
        """
        Start broadcast in blocking way.
        """
        self.load_data()
        self._publish()

    def _publish(self):
        while not self.stopped.is_set():
            time.sleep(self.rate_s)

            message = self._gen_data_frame()
            self.md["shape"] = message.shape
            self.md["type"] = message.dtype.name
            self.pub_sock.send_json(self.md, FLAGS | zmq.SNDMORE)
            self.pub_sock.send(
                message,
                FLAGS,
                copy=False,
            )

            self.iter += 1

    def close(self):
        """Set closing flag and stop listener."""
        self.stopped.set()


if __name__ == "__main__":
    df = "/sf/bernina/exp/25g_chapman/work/data/sim_raw.npy"
    if len(sys.argv) >= 2:
        df = sys.argv[1]
    rate = 1
    if len(sys.argv) >= 3:
        rate = sys.argv[2]
    publisher = DaqStreamEmulator(data_file=df, rate_s=rate)
    publisher.run()

