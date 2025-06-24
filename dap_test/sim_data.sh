#!/bin/bash

source /sf/jungfrau/applications/miniconda3/etc/profile.d/conda.sh
conda activate dap-clone

cd /das/work/p22/p22263/scripts/dap_test
python publisher.py