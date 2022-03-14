#   Cadence Plotting Utility

Zephan M. Enciso  
Intelligent MicroSystems Lab  

##  Usage

From the waveform viewer, export your data as a `.csv` file to the `data`
directory.  Make sure to enable the "Interpolate" option so each waveform has
the same time axis.  Then, invoke the main script as follows:

```python
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

