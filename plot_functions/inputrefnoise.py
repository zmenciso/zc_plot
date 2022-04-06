# Zephan M. Enciso
# Intelligent MicroSystems Lab

from plot_functions import replot
import pandas as pd
import numpy as np
import sys


def usage():
    print(f'''{sys.argv[0]} inputrefnoise INPUT [kwargs]
    fs=float        Set sample rate in Hz (default: 50e6)
    Ts=float        Set sample period in s, overrides fs (default: 1/fs)
    delay=float     Set delay before first sample (default: 0)
    Uses the same plotting kwargs as replot''')


def plot(df, kwargs):
    param = {
        'fs': 50e6,
        'Ts': None,
        'y': df.columns[1],
        'bins': df.columns[2],
        'delay': 9e-9
    }

    for arg in kwargs:
        key, value = arg.split('=')
        if key in param:
            param[key] = value

    param['fs'] = float(param['fs'])
    param['delay'] = float(param['delay'])

    if not param['Ts']:
        param['Ts'] = 1 / param['fs']
    else:
        param['Ts'] = float(param['Ts'])

    d_fill = pd.Series(np.empty(shape=(0), dtype=np.float64))

    for i in range(0, len(df), size := np.unique(df['x']).size):
        time = param['Ts'] + param['delay']
        samples = list()
        for index, series in df.iloc[i:i + size].iterrows():
            hue = series[param['bins']]
            if series['x'] >= time:
                samples.append(series[param['y']])
                time += param['Ts']

        d_fill = pd.concat([d_fill, pd.Series([hue, np.mean(samples)])],
                           axis=1,
                           ignore_index=True)

    pd_sampled = pd.DataFrame(d_fill.T.values,
                              columns=['x', param['y']]).iloc[1:, :]

    kwargs += [f'y={param["y"]}']
    replot.plot(pd_sampled, kwargs)
