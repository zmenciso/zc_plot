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

From the waveform viewer, export your data as a `.csv` file.  Make sure to
enable the "Interpolate" option so each waveform has the same time axis.  Then,
invoke the main script as follows:

```
./cadence_plot.py [OPTIONS] PLOT INPUT [kwargs]
    -h  --help      Display this message
    -v  --verbose   Enable verbose output
    -s  --summary  Choose filetype (default: `svg`)

    PLOT is the plot you wish to create, defined in `plot_functions.py`:
    gmid
    inputrefnoise
    replot
    ...

INPUT is the input data file, e.g. `data/my_data.csv`.
If no input and kwargs are given, prints the usage for the given PLOT.
```

This script can also do plotting with Maestro summary data instead of a
waveform.  In this case, use the `-s` or `--summary` switch and ensure that the
selected plotting function supports it.

To provide a multi-word kwarg, either enclose the entire kwarg definition in
quotes or just the value, e.g.:

```
./cadence_plot.py replot 'data.csv' 'xlabel=Time [s]'
OR
./cadence_plot.py replot 'data.csv' xlabel='Time [s]'
```

##  Writing Additional Plot Functions

Each new plot function should be defined in a different file in the
`plot_functions` directory.  This file must have a function called `plot` with
two mandatory arguments: `df`, the input Pandas DataFrame, and `kwargs`, which
is a list of additional arguments passed to the function.  This file must also
have a function called `usage` with no arguments.

```python
# Other function defs here

def usage():
    print('Interesting things about this program')

def plot(df, kwargs):
    sns.lineplot(...)
```

It is also possible to **call other plot functions**.  For example, using
`replot` is a convenient way to draw line plots without re-parsing the kwargs.

```python
from replot import plot

# Some DataFrame transformations here
kwargs.append('hue=my_new_metric')

plot(df, kwargs)
```

It is **recommended**, though not required, to expect each additional argument
to be of the form `key=value`, which makes parsing the `kwargs` trivial.  For
example:

```
./cadence_plot.py replot path/to/data.csv filetype=png logx=true hue=Vov
```

```python
kwargs = ['filetype=png', 'logx=true', 'hue=Vov']

param = dict(
    # Default values
    )

for arg in kwargs:
    key, value = arg.split('=')
    if key in param:
        param[key] = value

```
