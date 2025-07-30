import os
import sys
import time
from threading import Event

import numpy as np
import zmq
from Cython.Shadow import returns
from h5py import File

FLAGS = 0
DATA_PATH = "/sf/bernina/exp/25g_chapman/raw"
JF_DATASET = "data/JF07T32V02/data"


class DaqStreamEmulator:
    PORT = 60123
    HOST = "*"

    def __init__(
            self,
            scan_num: int,
            sleep_s: float,
            socket_type: int = zmq.PUSH
    ):
        self.sleep_s = sleep_s
        self.stopped = Event()

        zmq_context = zmq.Context()  # io_threads=4)
        self.pub_sock = zmq_context.socket(socket_type=socket_type)
        address = f"tcp://{self.HOST}:{self.PORT}"
        self.pub_sock.bind(address)

        self.data = None
        data_path = os.path.join(DATA_PATH, f"run{scan_num:04d}/raw_data")
        files = os.listdir(data_path)
        files.sort()
        self.files = [os.path.join(data_path, f) for f in files]
        self.md = {
            "shape": (2, 2),  # Empty frame
            "is_good_frame": True,
            "pedestal_file": "/sf/jungfrau/data/pedestal/JF07T32V02/20250721_012336.h5",
            "detector_name": "JF07T32V02",
            "gain_file": "/sf/jungfrau/config/gainMaps/JF07T32V02/gains.h5"
        }
        self.iter = 0
        self.o_index = 0
        self.i_index = 0
        self.current_file = None
        self.frames_in_current_file = None

    def load_frame(self):
        if self.current_file is None:
            self.current_file = self.files[self.o_index]
        if self.frames_in_current_file is None:
            with File(self.current_file, "r") as df:
                self.frames_in_current_file = df[JF_DATASET].shape[0]

        if self.i_index >= self.frames_in_current_file:
            self.i_index = 0
            self.o_index += 1
            self.current_file = self.files[self.o_index % len(self.files)]
            with File(self.current_file, "r") as df:
                self.frames_in_current_file = df[JF_DATASET].shape[0]

        with File(self.current_file, "r") as df:
            frame = df["data/JF07T32V02/data"][self.i_index]
        self.i_index += 1
        return frame

    def _gen_data_frame(self):
        im = np.ascontiguousarray(self.load_frame())
        return im

    def run(self):
        """
        Start broadcast in blocking way.
        """
        self._publish()

    def _publish(self):
        while not self.stopped.is_set():
            time.sleep(self.sleep_s)

            message = self._gen_data_frame()
            self.md["shape"] = message.shape
            self.md["type"] = message.dtype.name
            self.md["pulse_id"] = int(1e5 + self.iter)
            self.pub_sock.send_json(self.md, FLAGS | zmq.SNDMORE)
            self.pub_sock.send(
                message,
                FLAGS,
                copy=False,
            )
            #print(f"PUB im shape {message.shape} type {message.dtype.name}")
            self.iter += 1

    def close(self):
        """Set closing flag and stop listener."""
        self.stopped.set()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: `python real_publisher.py <scan_id> [<sleep_s>]`")
        exit(0)
    scan_id = int(sys.argv[1])
    sleep_s = 0.5
    if len(sys.argv) >= 3:
        sleep_s = float(sys.argv[2])
    publisher = DaqStreamEmulator(scan_num=scan_id, sleep_s=sleep_s)
    publisher.run()

