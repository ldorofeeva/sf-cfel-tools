import os
import h5py
import random

import numpy as np
import jungfrau_utils as ju

from sfdata import SFScanInfo


def generate_export_file_name(export_dir: str, scan_id: int) -> str:
    export_file_name = os.path.join(
        export_dir,
        f"scan{scan_id:04d}_proc_{random.randint(0, 1000):04d}.h5"
    )
    return export_file_name


def prepare_file(
        export_file_name: str,
        data_tag: str,
        frame_shape: list|tuple,
        sim_tag: str,
        log_tag: str,
        scan_info: SFScanInfo
) -> None:
    if os.path.exists(export_file_name):
        print(f"File {export_file_name} exists - skipping prepare")
    log_positions = scan_info.readbacks
    sim_positions = scan_info.values
    axes_names = scan_info.parameters['name']
    num_steps = len(log_positions)
    with h5py.File(export_file_name, "w") as export_f:
        export_f.create_dataset(data_tag, data=np.zeros((num_steps, *frame_shape)))
        export_f.create_dataset(sim_tag, data=np.asarray(sim_positions))
        export_f.create_dataset(log_tag, data=np.asarray(log_positions))
        export_f.attrs["axes"] = axes_names


def process_one_frame(
        jf_file_path: str,
        pedestal_file: str,
        gain_file: str,
        index: int,
        out_fd: h5py.File,
        data_tag: str,
        num_avg: int,
        roi_1: list[int],
        roi_2: list[int],
        raw: bool = True
):
    _, fname = os.path.split(jf_file_path)
    conversion = False
    if raw:
        jf_file_path = jf_file_path.replace("/data/acq", "/raw_data/acq")
        conversion = True
    with ju.File(
            jf_file_path,
            pedestal_file=pedestal_file,
            gain_file=gain_file,
            conversion=conversion,
    ) as juf:
        avg_img = np.average(
            juf[:num_avg,
                roi_1[0]:roi_1[1],
                roi_2[0]:roi_2[1]],
            axis=0)
    out_fd[data_tag][index] = avg_img
    print(f"\tExported file {fname} at #{index:04d}")