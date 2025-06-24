# SF CFEL tools

A set of convenience scripts to use for data processing at SwissFEL during CFEL/Chapman CBD experiment.

### dap-test

Scripts and instructions to test DAP pipeline on PSI RA cluster

See documentation [here](dap_test/README.md)

### scan-exporter

Tools for exporting 2D scan Jungfrau data into format readable by `pyrost` library - for Speckle-Tracking

See documentation [here](scan_exporter/README.md)

### RA documentation

RA is the PSI cluster that will be used primarily for online-ish processing

Below is some unofficial troubleshooting advises and workarounds. 

#### Jupyterra


#### Running Jupyter notebook

If jupyter hub is completely doown (which I have experienced), below is the instuctions to run 
a Jupyter notebook in an interactive session

1. Submit an interactive job

2. Run jupyter notebook as follows
```
# Load anaconda module
module load anaconda/2024.08

# Activate environment
conda activate pyrost-jupy

# Add necessary scripts location to PYTHONPATH
export PYTHONPATH="<your_scripts_dir>"

# Run notebook
jupyter notebook --no-browser --ip=* --port=5009
```

`--no-browser` does not attempt to open non-existing browser on computation node
`--ip=*` allows connecting from a different host (RA login node)
`--port=5009` a likely unused port, chosen for convenience of one-to-one port mapping (see below) 
that allows to copy notebook link from command line and paste into browser on login node.

3. In a separate shell, enable port forwarding

as follows:
```
ssh -L 5009:<ra-compute-node>:5009 <ext-account_n>@<ra-compute-node>
```

example:
```
ssh -L 5009:ra-c-050:5009 ext-dorofe_e@ra-c-050
```


#### Regular MPI jobs

#### Nodes Blacklist (may be out of date)