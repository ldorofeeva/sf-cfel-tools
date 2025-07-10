# DAP test

The task is three-fold:

1. Simulate JF frames stream
2. Subscribe to stream from a local version of DAP - for processing 
and further streaming processed results to visualization software 
3. Subscribe to visualization stream from a local version of streamvis


### 1. DAP worker

Updated Code directory: `/das/work/p22/p22263/git/dap`
##### 1.0 Start interactive job on RA:
```
srun --partition=day --ntasks=32 --exclusive --mem=0 --pty bash -i
```

##### 1.1 Launch DAP:
```
conda activate dap-sf

cd /das/work/p22/p22263/git/dap
export PYTHONPATH=`pwd` 
        
python dap/worker.py --backend_address tcp://127.0.0.1:60123 \
        --visualisation_host 127.0.0.1 --visualisation_port 60124 \
        --peakfinder_parameters ./dap/example_settings.json
```

### 2. Frames stream simulation

##### 2.0 SSH to RA job node if not done so yet:
`ssh <ra_cpu_node>`

##### 2.1 Launch stream simulator:

By default, simulated data from Chufeng are used
```
conda activate dap-sf

cd /das/work/p22/p22263/git/sf-cfel-tools/dap_test
python publisher.py
```

Example launch with a different source data file:
```
python publisher.py $DATA/raw/run0001/raw_data/acq0001.JF07T32V02.h5
```

### 3. Streamvis

##### 3.0 SSH to RA job node with port-forwarding
```
ssh -L 5006:<ra_cpu_node>:5006 <ext-account_n>@<ra_cpu_node>
```

Example:
```
ssh -L 5006:ra-c-051:5006 ext-dorofe_e@ra-c-051
```

##### 3.1 Launch streamvis app:

```
source /sf/jungfrau/applications/miniconda3/etc/profile.d/conda.sh
conda activate streamvis

cd /das/work/p22/p22263/git/streamvis

# Optionally - deploy local changes
# pip install .

streamvis cbd --stream-format jfcbd --connection-mode bind --address tcp://*:60124
```

### 4. View streamvis in browser on Ra login node 

Go to: `http://localhost:5006/`

