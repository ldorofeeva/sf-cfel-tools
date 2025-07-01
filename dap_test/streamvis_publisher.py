import sys
from math import sqrt, pow
from threading import Thread

import numpy as np
import zmq

from dap_test.publisher import DaqStreamEmulator


def line_len(x0, y0, x1, y1):
    return sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))


class ProcessedDataStreamEmulator(DaqStreamEmulator):
    PORT = 9001
    HOST = "127.0.0.1"

    def __init__(self, start_pulse_id: int, data_file: str, rate_s: float):
        super().__init__(data_file, rate_s, socket_type=zmq.PUB)
        self.start_pulse_id = start_pulse_id
        self.md = {
            "shape": (2, 2),  # Empty frame
            "is_good_frame": True,
            "pedestal_file": "/sf/jungfrau/data/pedestal/JF07T32V01/20230414_100746.h5",
            "detector_name": "JF07T32V01",
            "gain_file": "/sf/jungfrau/config/gainMaps/JF07T32V01/gains.h5"
        }
        self.iter = 0

    def load_data(self):
        self.data = np.load(self.data_file)

    def _gen_data_frame(self):
        idx = self.iter % self.data.shape[0]
        im = np.ascontiguousarray(self.data[idx, ::4, ::4])

        n_spots = np.random.randint(1, 55)
        is_hit_frame = n_spots > 5

        intensities_range = (int(np.average(im[im>0])), int(np.max(im))  -1)
        intensities = []
        streaks_t = []
        streak_lens = []

        for i in range(n_spots):
            x0 = float(np.random.randint(50, im.shape[1] - 50)) + np.random.rand()
            y0 = float(np.random.randint(50, im.shape[0] - 50)) + np.random.rand()

            x_len = np.random.randint(10, 50)
            y_len = np.random.randint(10, 50)

            line = [x0 - x_len/2, y0 - y_len/2, x0 + x_len/2, y0 + y_len/2]
            streak_len = line_len(*line)
            intensity = (float(np.random.randint(*intensities_range)) + np.random.rand()) * streak_len
            intensities.append(intensity)
            streak_lens.append(streak_len)
            streaks_t.append(line)

        streaks = np.asarray(streaks_t).T.tolist()

        pulse_mixup = {
            0: 0,
            1: 2,
            2: 3,
            3: 1,
            4: 5,
            5: 4,
            6: 6,
            7: 9,
            8: 7,
            9: 8,
        }
        pulse_id = int( self.iter * 100 + np.random.randint(0, 9) + self.start_pulse_id)

        # pulse_id = int((pulse_mixup.get(idx, idx) + self.iter // self.data.shape[0]) * 10 + 1e5)

        _md = {
            'is_good_frame': True,
            'pedestal_file': '/home/edorofee/BeamlineData/SwissFEL/JU/20230414_100746.h5',
            'detector_name': 'JF07T32V01',
            'gain_file': '/home/edorofee/BeamlineData/SwissFEL/JU/gains.h5',
            'type': 'uint16',
            'beam_center_x': 2107.5,
            'beam_center_y': 2216.0,
            'detector_distance': 0.5092,
            'do_peakfinder_analysis': 1,
            'hitfinder_adc_thresh': 20.0,
            'hitfinder_min_pix_count': 3,
            'hitfinder_min_snr': 4.0,
            'apply_additional_mask': 0,
            'npeaks_threshold_hit': 9,
            'beam_energy': 11993.610318642704,
            # 'do_whitefield_correction': 1,
            # 'do_intensity_normalization': 0,
            # 'wf_data_file': '/das/work/p22/p22263/whitefield/wf_div.h5',
            # 'wf_method': 'div',
            # 'do_streakfinder_analysis': 0,
            # 'sf_structure_radius': 3, 'sf_structure_rank': 2, 'sf_min_size': 4,
            # 'sf_vmin': 0.4, 'sf_npts': 3, 'sf_xtol': 0.2,
            'number_of_spots': 0,
            'is_hit_frame': is_hit_frame,
            'laser_on': True,
            'saturated_pixels': 0, 'saturated_pixels_x': [], 'saturated_pixels_y': [],
            'streak_lengths': streak_lens,
            'bragg_counts': intensities,  # [39.351688385009766, 1497.404541015625, 262.4278869628906],
            'number_of_streaks': len(streaks_t),
            'streaks': streaks,
            'is_white_field_corrected': True,
            'pulse_id': pulse_id,
        }
        print(pulse_id)
        self.md.update(_md)
        return im

    def run(self):
        self.load_data()
        Thread(target=self._publish).start()


if __name__ == "__main__":
    start_pulse_id = 552300
    if len(sys.argv) >= 2:
        start_pulse_id = int(sys.argv[1])
    rate = 0.5
    if len(sys.argv) >= 3:
        rate = float(sys.argv[2])
    df = "/home/edorofee/BeamlineData/SwissFEL/JU/i3c_pat_sim.npy"
    if len(sys.argv) >= 4:
        df = sys.argv[3]
    publisher = ProcessedDataStreamEmulator(start_pulse_id=start_pulse_id, data_file=df, rate_s=rate)
    publisher.run()

