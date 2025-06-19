import json
import os
import sys
import time

import h5py
import numpy as np
from mpi4py import MPI
from sfdata import SFScanInfo

from scan_exporter.util import prepare_file, generate_export_file_name, process_one_frame

if __name__ == "__main__":
    comm = MPI.COMM_WORLD

    rank = comm.Get_rank()  # The process ID (integer 0-3 for 4-process run)
    size = comm.Get_size()

    if len(sys.argv) < 2:
        if rank == 0:
            print(f"Usage: python export.py <scan_id>")
        exit(-1)
    scan_id = int(sys.argv[1])

    if rank == 0:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "settings.json"), "r") as f:
            settings = json.load(f)
        scan_name = f"run{scan_id:04d}"

        export_file_name = generate_export_file_name(settings["export_dir"], scan_id)

        scan_info = SFScanInfo(os.path.join(
            settings["source_dir"], scan_name, "meta/scan.json"
        ))
        print(f"Exporting Scan with parameters:\n"
              f"{scan_info.parameters}")

        num_steps = len(scan_info.readbacks)
        files = scan_info.files[:num_steps]

        shape = settings["jf_shape"]
        for dim in [1, 2]:
            if settings.get(f"roi_{dim}", None) is not None:
                shape[dim - 1] = settings[f"roi_{dim}"][1] - settings[f"roi_{dim}"][0]
            else:
                settings[f"roi_{dim}"] = [0, shape[dim - 1]]

        prepare_file(
            export_file_name=export_file_name,
            data_tag=settings["st_data_tag"],
            frame_shape=shape,
            sim_tag=settings["st_sim_pos_tag"],
            log_tag=settings["st_log_pos_tag"],
            scan_info=scan_info
        )
        settings.update({
            "scan_name": scan_name,
            "file_name": export_file_name,
            "num": num_steps,
            "shape": shape
        })
        print(f"Running with settings:{settings}")

        settings.update({"files": files})
    else:
        settings = None

    settings = comm.bcast(settings, root=0)

    t0 = time.time()
    indices = np.array_split(np.arange(settings["num"]), size)[rank]
    # num_avg = settings["num_avg"]
    # roi_1_min, roi_1_max = settings[f"roi_1"]
    # roi_2_min, roi_2_max = settings[f"roi_2"]

    with h5py.File(settings["file_name"], "a", driver='mpio', comm=MPI.COMM_WORLD) as export_f:
        # export_f.create_dataset(
        #     settings["st_data_tag"],
        #     data=np.zeros((settings["num"], *settings["shape"]))
        # )

        for index in indices:
            file_path = next((f for f in settings["files"][index] if settings["detector_name"] in f), None)
            if file_path is None:
                print(f"No files for {settings['detector_name']} in scan at {index}!")
            else:
                process_one_frame(
                    jf_file_path=file_path,
                    pedestal_file=settings["jf_pedestal"],
                    gain_file=settings["jf_gain"],
                    index=index,
                    out_fd=export_f,
                    data_tag=settings["st_data_tag"],
                    num_avg=settings["num_avg"],
                    roi_1=settings[f"roi_1"],
                    roi_2=settings[f"roi_2"]
                )

            #
            # _, fname = os.path.split(file_path)
            # print(f"{rank} converting {fname} at {index}")
            # conversion = False
            # if settings["raw"]:
            #     file_path = file_path.replace("/data/acq", "/raw_data/acq")
            #     conversion = True
            # with ju.File(
            #         file_path,
            #         pedestal_file=settings["jf_pedestal"],
            #         gain_file=settings["jf_gain"],
            #         # conversion=conversion,
            # ) as juf:
            #     avg_img = np.average(juf[
            #                          :num_avg,
            #                          roi_1_min:roi_1_max,
            #                          roi_2_min:roi_2_max
            #                          ], axis=0)
            # print(f"\t{rank} Read file {fname} at #{index:04d}")
            # export_f[settings["st_data_tag"]][index] = avg_img

        comm.Barrier()

    if rank == 0:
        print(f"Exported to {settings['file_name']}\n"
              f"Export completed in {time.time() - t0} seconds on {size} CPUs")
