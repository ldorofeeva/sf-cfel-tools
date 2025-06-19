# DAP test

The task is three-fold:

1. Simulate JF frames stream
2. Subscribe to stream from a local version of DAP - for processing 
and further streaming processed results to visualization software 
3. Subscribe to visualization stream from a local version of streamvis

### 0. Interactive session on RA
  Example:
```
srun --partition=day --ntasks=40 --exclusive --mem=0 --pty bash -i
```

*NOTE: all of the following should be done on RA node assigned to the job*

### 1. Frames stream simulation
##### 1.0 SSH to RA job node if not done so yet:
`ssh <ra_cpu_node>`

Data file example (lysosime, default):
```
/das/work/p22/p22263/data/lyso009a_0087.JF07T32V01.h5
```

##### 1.1 Launch stream simulator:
```
source /sf/jungfrau/applications/miniconda3/etc/profile.d/conda.sh
conda activate dap-clone

cd /das/work/p22/p22263/scripts/dap_test
python publisher.py
```

Example launch with a different source data file:
```
`python publisher.py \
    /sf/bernina/exp/example_data/Ge_tt/scan_data/run0132_Ge_delay_scan.json_step0000.JF07T32V01.h5 \
    data/JF07T32V01/data`
```

Simulated data - coming soon from Chufeng

### 2. DAP worker

Updated Code directory: `/das/work/p22/p22263/git/dap-clone`


##### 2.0 SSH to RA job node if not done so yet:
`ssh <ra_cpu_node>`

##### 2.1 Launch DAP:
```
source /sf/jungfrau/applications/miniconda3/etc/profile.d/conda.sh
conda activate dap-clone

cd /das/work/p22/p22263/git/dap-clone
export PYTHONPATH=`pwd` 
        
python dap/worker.py --backend_address tcp://127.0.0.1:60123 \         
    --visualisation_host 127.0.0.1 --visualisation_port 60124 \         
    --peakfinder_parameters ./dap/example_settings.json
```

### 3. Streamvis

##### 3.0 SSH to RA job node if not done so yet:
`ssh <ra_cpu_node>`

##### 3.1 Launch streamvis app:

```
source /sf/jungfrau/applications/miniconda3/etc/profile.d/conda.sh
conda activate streamvis

streamvis bernina --connection-mode bind --address tcp://*:60124
```

### 4. View streamvis in browser on Ra login node 
```
ssh -L 5006:<ra_cpu_node>:5006 <ext-account_n>@<ra_cpu_node>
```

Example:
```
ssh -L 5006:ra-c-051:5006 ext-dorofe_e@ra-c-051
```

Go to:

`http://localhost:5006/`

