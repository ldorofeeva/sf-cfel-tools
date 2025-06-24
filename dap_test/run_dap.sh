#!/bin/bash

source /sf/jungfrau/applications/miniconda3/etc/profile.d/conda.sh
conda activate dap-clone

cd /das/work/p22/p22263/git/dap
python dap/worker.py --backend_address tcp://127.0.0.1:60123 \
        --visualisation_host 127.0.0.1 --visualisation_port 60124 \
        --peakfinder_parameters ./params.json