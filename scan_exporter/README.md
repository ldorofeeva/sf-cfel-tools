## SwissFEL exporter

Exporter comes in two flavours:
- an independent MPI script (to run from shell on cluster nodes)
- a class using multiprocessing (to use from jupyter notebooks)

### Update Settings

Go to common scripts dir:

```
cd /sf/bernina/exp/25g_chapman/work/scripts/scan_exporter
```

Edit `settings.json`.

Example settings:
```
{
  "detector_name": "JF07T32V01",
  "jf_pedestal": "/sf/bernina/exp/example_data/Ge_tt/pedestal_20190304_0545.JF07T32V01.res.h5",
  "jf_gain": "/sf/jungfrau/config/gainMaps/JF07T32V01/gains.h5",
  "jf_shape": [4432, 4215],
  "source_dir": "/sf/bernina/exp/25g_chapman/work/test/raw/",
  "export_dir": "/sf/bernina/exp/25g_chapman/work/test/work/",
  "st_data_tag": "/entry/data/data",
  "st_sim_pos_tag": "/entry/positions/sim_positions",
  "st_log_pos_tag": "/entry/positions/log_positions",
  "roi_2": [2500, 2800],
  "roi_1": [200, 500],
  "num_avg": 100,
  "raw": 1
}

```

### Run in an interactive session as a script

Start interactive session (example below is for 4 hours):

```
srun --partition=day --ntasks=32 --mem=0 --exclusive --pty bash -i
```

Activate environment:

```
module load anaconda/2024.08
conda activate pyrost
```

Go to common scripts dir:

```
cd /sf/bernina/exp/25g_chapman/work/scripts/scan_exporter
```


Run exporter with scan id argument:
```
mpiexec -np 10 python exporter.py 1
```

Example output:
```
Exporting Scan with parameters:
{'expected_total_number_of_steps': 97, 'name': ['delay'], 'scan_name': 'run0078_'}
Running with settings:{'detector_name': 'JF07T32V01', 'jf_pedestal': '/sf/bernina/exp/example_data/Ge_tt/pedestal_20190304_0545.JF07T32V01.res.h5', 'jf_gain': '/sf/jungfrau/config/gainMaps/JF07T32V01/gains.h5', 'jf_shape': [300, 300], 'source_dir': '/sf/bernina/exp/25g_chapman/work/test/raw/', 'export_dir': '/sf/bernina/exp/25g_chapman/work/test/work/', 'st_data_tag': '/entry/data/data', 'st_sim_pos_tag': '/entry/positions/sim_positions', 'st_log_pos_tag': '/entry/positions/log_positions', 'roi_2': [2500, 2800], 'roi_1': [200, 500], 'num_avg': 100, 'raw': 1, 'scan_name': 'run0001', 'file_name': '/sf/bernina/exp/25g_chapman/work/test/work/scan0001_proc_0245.h5'

...

    5 Exported file run0132_Ge_delay_scan.json_step0030.JF07T32V01.h5 at #0029
    4 Exported file run0132_Ge_delay_scan.json_step0025.JF07T32V01.h5 at #0024
	0 Exported file run0132_Ge_delay_scan.json_step0005.JF07T32V01.h5 at #0004
Exported to /sf/bernina/exp/25g_chapman/work/test/work/scan0001_proc_0245.h5
Export completed in 68.40982913970947 seconds on 10 CPUs

```

### Use from jupyter notebook 

```
from scan_exporter import *

exporter = JFCFELExporter(
    raw_data_path="/sf/bernina/exp/25g_chapman/work/test/raw/",
    export_data_path="/sf/bernina/exp/25g_chapman/work/test/work/",
    # detector_name="JF01T03V01",
    # jf_pedestal="/sf/jungfrau/data/pedestal/JF01T03V01/20250507_222051.h5",
    # jf_gain="/sf/jungfrau/config/gainMaps/JF01T03V01/gains.h5",
    # jf_shape=(1614, 1030)
)

exporter.load_scan(scan_id=1)

exporter.export_scan(num_avg=5, overwrite=True, raw=True, processes=4)
```
