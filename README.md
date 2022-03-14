#   Cadence Plotting Utility

Zephan M. Enciso  
Intelligent MicroSystems Lab  

##  Dependencies

These utilities have been tested with the following software versions:
  - `python` == 3.9.7
  - `matplotlib` == 3.5.1
  - `jedi` == 0.18.1
  - `scipy` == 1.8.0
  - `numpy` == 1.22.2
  - `pandas` == 1.4.0

##  Usage

From the waveform viewer, export your data as a `.csv` file to the `data`
directory.  Make sure to enable the "Interpolate" option so each waveform has
the same time axis.  Then, invoke the main script as follows:

```
./cadence_plot.py [OPTIONS] PLOT INPUT
    -h  --help      Display this message
    -v  --verbose   Enable verbose output
    -f  --filetype  Choose filetype (default: `svg`)

    PLOT is the plot you wish to create, defined in `plot_functions.py`:
    gmid
    inputrefnoise

    INPUT is the input data file, e.g. `data/my_data.csv`
```

##  Writing Additional Plot Functions

