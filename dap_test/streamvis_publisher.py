import sys
from threading import Thread

import numpy as np
import zmq

from dap_test.publisher import DaqStreamEmulator


class ProcessedDataStreamEmulator(DaqStreamEmulator):
    PORT = 9001
    HOST = "127.0.0.1"

    def __init__(self, data_file: str, rate_s: int):
        super().__init__(data_file, rate_s, socket_type=zmq.PUB)

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
        im = super()._gen_data_frame()

        n_spots = np.random.randint(1, 15)
        is_hit_frame = n_spots > 5
        spots_x = []
        spots_y = []
        intensities_range = (int(np.average(im)), int(np.max(im))  -1)
        intensities = []

        streaks_t = []

        for i in range(n_spots):
            x0 = float(np.random.randint(250, im.shape[1] - 250)) + np.random.rand()
            y0 = float(np.random.randint(250, im.shape[0] - 250)) + np.random.rand()
            spots_x.append(x0)
            spots_y.append(y0)
            intensities.append(float(np.random.randint(*intensities_range)) + np.random.rand())
            streaks_t.append([x0 - 100, y0 - 100, x0 + 100, y0 + 100])


        streaks_t = [[1383.1565403694399, 1902.7698115768096, 1383.2200199736349, 1891.6489953717617],
                    [1299.1540283030943, 2301.465827278728, 1299.2497288611128, 2290.4046077735406],
                    [991.1565611825587, 857.311495292752, 991.1916344302091, 846.3819865583788],
                    [3703.1694468115484, 3106.1499679647804, 3703.1264771958085, 3095.330848542574],
                    [1387.1138451409165, 1901.0564600728587, 1387.108440428609, 1890.3828175673796],
                    [3700.1147396059, 3103.982179427265, 3700.1218971381973, 3093.3870976750213],
                    [1903.130697151182, 2079.975271614859, 1903.1584162111242, 2069.378084535801],
                    [1541.080690678922, 3989.9785768530915, 1541.1811666203125, 3979.4530708871885],
                    [3267.08043339057, 4038.9356945146915, 3267.156246100426, 4028.437449736685],
                    [3257.075477567806, 4043.897999716471, 3257.1522202419255, 4033.4551370739377],
                    [3261.0732833879665, 4040.859536814362, 3261.159369116428, 4030.4347389031896],
                    [3263.070454300261, 4042.786251873229, 3263.152920426425, 4032.3334911467455],
                    [3259.064534675581, 4042.7560717464416, 3259.1502443695654, 4032.3533196852145],
                    [3247.059780492649, 4048.7316661666955, 3247.1489690823246, 4038.3734848577687],
                    [3237.056327150681, 4054.707301096757, 3237.1506114114804, 4044.359793145105],
                    [3243.051691746385, 4050.6864573463126, 3243.156602947464, 4040.3511400997513],
                    [3239.047842955299, 4053.664074637856, 3239.1561221372235, 4043.341589083432],
                    [1303.0433883074231, 2299.6251361732852, 1303.1225330229256, 2289.3486394946935],
                    [3251.0416993383983, 4045.601149015646, 3251.1297783630484, 4035.3328773242156],
                    [3253.0384825832184, 4047.577004393913, 3253.1326997765923, 4037.2573738498468],
                    [3229.0363485435264, 4058.5423214359193, 3229.1162450514985, 4048.2457719453146],
                    [3233.0355955452487, 4055.527104349378, 3233.1193447151427, 4045.2369842566727],
                    [987.0361039798612, 856.5114195767965, 987.1320648306154, 846.2346251214499]]
        streaks = np.asarray(streaks_t).T.tolist()

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
            'laser_on': False,
            'saturated_pixels': 0, 'saturated_pixels_x': [], 'saturated_pixels_y': [],
            'spot_x': spots_x,  # [1385.9989013671875, 1909.938720703125, 1301.97021484375],
            'spot_y': spots_y,  # [1896.001220703125, 2058.712646484375, 2293.52685546875],
            'spot_intensity': intensities,  # [39.351688385009766, 1497.404541015625, 262.4278869628906],
            'number_of_streaks': len(streaks_t),
            'streaks': streaks,
            'is_white_field_corrected': True
        }

        self.md.update(_md)
        return im

    def run(self):
        self.load_data()
        Thread(target=self._publish).start()



if __name__ == "__main__":
    df = "/home/edorofee/BeamlineData/SwissFEL/JU/i3c_pat_sim.npy"
    if len(sys.argv) >= 2:
        df = sys.argv[1]
    rate = 1
    if len(sys.argv) >= 3:
        rate = sys.argv[2]
    publisher = ProcessedDataStreamEmulator(data_file=df, rate_s=rate)
    publisher.run()

