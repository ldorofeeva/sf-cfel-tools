import sys
import time
from threading import Event

import numpy as np
import zmq
from h5py import File
from streak_finder.ndimage import draw_lines

PORT = 60123
FLAGS = 0

immax = 300

n_lines = 100
length = 30
width = 3.5

class DaqStreamEmulator:
    def __init__(
            self,
            rate_s: int = 1,
            data_file="/sf/bernina/exp/25g_chapman/work/data/lyso009a_0087.JF07T32V01.h5",
            dset_tag="data/data"
    ):
        self.host = "*"
        self.rate_s = rate_s
        self.stopped = Event()

        zmq_context = zmq.Context()  # io_threads=4)
        self.pub_sock = zmq_context.socket(zmq.PUSH)
        address = f"tcp://{self.host}:{PORT}"
        self.pub_sock.bind(address)

        self.data = None
        self.data_file = data_file
        self.dset_tag = dset_tag
        self.md = {
            "shape": (2, 2),  # Empty frame
            "is_good_frame": True,
            "pedestal_file": "/sf/bernina/exp/example_data/Ge_tt/pedestal_20190304_0545.JF07T32V01.res.h5",
            "detector_name": "JF07T32V01",
            "gain_file": "/sf/jungfrau/config/gainMaps/JF07T32V01/gains.h5"
        }
        self.iter = 0

    def load_data(self):
        if self.data_file.endswith(".h5"):
            with File(self.data_file, "r") as df:
                self.data = np.asarray(df[self.dset_tag])[:50]
        elif self.data_file.endswith(".npy"):
            self.data = np.load(self.data_file)

    def _gen_data_frame(self):
        idx = self.iter % self.data.shape[0]
        im = np.ascontiguousarray(self.data[idx])

        rng = np.random.default_rng(immax)
        shape = im.shape
        centers = np.array([[shape[-1]], [shape[-2]]]) * rng.random((2, n_lines))
        lengths = length * rng.random((n_lines,))
        thetas = 2 * np.pi * rng.random((n_lines,))
        x0, y0 = centers
        lines = np.stack((x0 - 0.5 * lengths * np.cos(thetas),
                         y0 - 0.5 * lengths * np.sin(thetas),
                         x0 + 0.5 * lengths * np.cos(thetas),
                         y0 + 0.5 * lengths * np.sin(thetas),
                         width * np.ones(n_lines)), axis=1)
        return draw_lines(lines, shape, kernel='biweight') + im

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
    df = "/sf/bernina/exp/25g_chapman/work/data/lyso009a_0087.JF07T32V01.h5"
    if len(sys.argv) >= 2:
        df = sys.argv[1]
    dst = "data/data"
    if len(sys.argv) >= 3:
        dst = sys.argv[2]
    publisher = DaqStreamEmulator(data_file=df, dset_tag=dst)
    publisher.run()
