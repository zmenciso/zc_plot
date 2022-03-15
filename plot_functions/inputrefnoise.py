# Zephan M. Enciso
# Intelligent MicroSystems Lab

import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import sys


def usage():
    print('''inputrefnoise INPUT [kwargs]
    fs=float        Set sample rate in Hz (default: 50e6)
    Ts=float        Set sample period in s, overrides fs (default: 1/fs)
    delay=float     Set delay before first sample (default: 0)
    s=float         Set size of point (default: 10)
    size=tuple      Change figsize (default: 18/3,19/3)
    alpha=float     Change alpha (default: 0.5)
    bbox=bool       Enable/disable bbox for legend (default: True)
    xlabel=str      Change x axis label (default: 'x')
    ylabel=str      Change y axis label (default: y)
    xlim=tuple      Change xlim (default: full range)
    filetype=str    Change filetype (default: svg)
    filename=str    Custom filename''')


def plot(df, kwargs):
    fs = 50e6
    Ts = None
    figsize = (18/3, 9/3)
    alpha = 0.8
    bbox = False
    filetype = 'svg'
    filename = None
    s = 10

    xlim = (df['x'].iloc[0], df['x'].iloc[-1])
    y = df.columns[1]
    bins = df.columns[2]
    xlabel = bins
    ylabel = y
    delay = 9e-9

    for arg in kwargs:
        key, value = arg.split('=')

        if key == 'fs':
            fs = float(value)
        elif key == 'delay':
            delay = float(value)
        elif key == 'Ts':
            Ts = float(value)
        elif key == 'delay':
            delay = float(value)
        elif key == 's':
            s = float(value)
        elif key == 'size':
            figsize = tuple(map(float, value.split(',')))
        elif key == 'alpha':
            alpha = float(value)
        elif key == 'bbox':
            bbox = bool(value)
        elif key == 'xlabel':
            xlabel = value
        elif key == 'ylabel':
            ylabel = value
        elif key == 'xlim':
            xlim = tuple(map(float, value.split(',')))
        elif key == 'filetype':
            filetype = value
        elif key == 'filename':
            filename = value
        else:
            print(f'ERROR: Unknown kwarg {key}', file=sys.stderr)

    plt.figure(figsize=figsize)

    if not Ts:
        Ts = 1 / fs

    d_fill = pd.Series(np.empty(shape=(0), dtype=np.float64))

    for i in range(0, len(df), size := np.unique(df['x']).size):
        time = Ts + delay
        samples = list()
        for index, series in df.iloc[i:i+size].iterrows():
            hue = series[bins]
            if series['x'] >= time:
                samples.append(series[y])
                time += Ts

        d_fill = pd.concat([d_fill, pd.Series([np.mean(samples), hue])],
                axis=1, ignore_index=True)

    pd_sampled = pd.DataFrame(d_fill.T.values, columns=[y, bins])
    sns.scatterplot(data=pd_sampled, x=bins, y=y, alpha=alpha, edgecolor=None, s=s)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if bbox:
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles,
                   labels,
                   loc='upper left',
                   bbox_to_anchor=(1.02, 1),
                   title=hue,
                   borderaxespad=0)

    plt.tight_layout()
    if filename:
        plt.savefig(f'{filename}.{filetype}')
    else:
        plt.savefig(
            f'{y}_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}.{filetype}')
    plt.xlim(xlim)
