import os
import time
import json
from functools import partial
from multiprocessing import Pool, Manager, current_process

import h5py
import jungfrau_utils as ju
import numpy as np
from sfdata import SFScanInfo

from scan_exporter.constants import (
    SOURCE_DIR, EXPORT_DIR,
    DETECTOR_NAME,
    JF_PEDESTAL, JF_GAIN, JF_SHAPE,
    ST_DATA_TAG, ST_SIM_POS_TAG, ST_LOG_POS_TAG
)
from scan_exporter.util import prepare_file, generate_export_file_name


class JFCFELExporter:
    def __init__(
            self,
            settings_file=None
    ):
        if settings_file is None:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            settings_file = os.path.join(dir_path, "settings.json")
        with open(settings_file, "r") as f:
            self.settings = json.load(f)
        self.jf_gain = self.settings.get("jf_gain", JF_GAIN)
        self.jf_shape = self.settings.get("jf_shape", JF_SHAPE)
        self.jf_pedestal = self.settings.get("jf_pedestal", JF_PEDESTAL)
        self.detector_name = self.settings.get("detector_name", DETECTOR_NAME)
        self.export_dir = self.settings.get("export_dir", EXPORT_DIR)
        self.source_dir = self.settings.get("source_dir", SOURCE_DIR)
        self.st_data_tag = self.settings.get("st_data_tag", ST_DATA_TAG)
        self.st_sim_pos_tag = self.settings.get("st_sim_pos_tag", ST_SIM_POS_TAG)
        self.st_log_pos_tag = self.settings.get("st_log_pos_tag", ST_LOG_POS_TAG)

        self.scan_info: SFScanInfo | None = None
        self.scan_id = None
        self.export_file_name = None
        self.scan_name = None

    def __repr__(self):
        s = f"Source directory:\n\t{self.source_dir}\n"
        s += f"Target directory:\n\t{self.export_dir}\n"
        s += f"Detector:\n\t{self.detector_name}\n\tShape: {self.jf_shape}\n\tPedestal: {self.jf_pedestal}\n"
        s += "Curent Scan Info:\n"
        if self.scan_info is None:
            s += "\tNo scan info loaded!\n"
        else:
            s += f"{self.scan_info.parameters}"
        return s

    def load_scan(self, scan_id) -> None:
        self.scan_id = scan_id
        self.scan_name = f"run{self.scan_id:04d}"
        self.export_file_name = generate_export_file_name(
            export_dir=self.export_dir, scan_id=self.scan_id
        )
        self.scan_info = SFScanInfo(os.path.join(self.source_dir, self.scan_name, "meta/scan.json"))

    def export_scan(self, num_avg=100, processes=1, overwrite=False, raw=False) -> str | None:
        if self.scan_info is None:
            print(f"No scan info loaded!")
            return

        print(f"Exporting Scan with parameters:\n"
              f"{self}")
        log_positions = self.scan_info.readbacks
        sim_positions = self.scan_info.values
        axes_names = self.scan_info.parameters['name']
        num_steps = len(log_positions)
        shape = self.jf_shape
        for dim in [1,2]:
            if self.settings.get(f"roi_{dim}", None) is not None:
                shape[dim-1] = self.settings[f"roi_{dim}"][1] - self.settings[f"roi_{dim}"][0]
            else:
                self.settings[f"roi_{dim}"] = [0, shape[dim-1]]

        prepare_file(
            export_file_name=self.export_file_name,
            data_tag=self.st_data_tag,
            frame_shape=shape,
            sim_tag=self.st_sim_pos_tag,
            log_tag=self.st_log_pos_tag,
            scan_info=self.scan_info
        )

        t0 = time.time()

        with Manager() as manager:
            # create the shared lock
            lock = manager.Lock()
            exporter = partial(self._export_one_jf_file, raw, num_avg, lock)
            with Pool(processes=processes, ) as pool:
                pool.map(exporter, range(num_steps))
                pool.close()
                pool.join()

        print(f"Scan {self.scan_name} successfully exported to {self.export_file_name}.\n"
              f"Export completed in {time.time() - t0} seconds on {processes} CPUs")
        return self.export_file_name

    def _export_one_jf_file(self, raw, num_avg, lock, index):
        file_path = next((f for f in self.scan_info.files[index] if self.detector_name in f), None)
        if file_path is None:
            print(f"No files for {self.detector_name} in scan {self.scan_name}!")
            return
        conversion = False
        if raw:
            file_path = file_path.replace("/data/acq", "/raw_data/acq")
            conversion = True

        roi_1_min, roi_1_max = self.settings[f"roi_1"]
        roi_2_min, roi_2_max = self.settings[f"roi_2"]

        me = current_process().name
        with ju.File(
                file_path,
                pedestal_file=self.jf_pedestal,
                gain_file=self.jf_gain,
                conversion=conversion,
        ) as juf:
            avg_img = np.average(juf[
                                 :num_avg,
                                 roi_1_min:roi_1_max,
                                 roi_2_min:roi_2_max
                                 ], axis=0)
        with lock:
            with h5py.File(self.export_file_name, "a") as export_f:
                export_f[self.st_data_tag][index] = avg_img
        print(f"\t{me} Processed file #{index:04d}")