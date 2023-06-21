# Zephan M. Enciso
# Intelligent MicroSystems Lab

# This function is painfully slow because the sampling logic is terrible
# TODO: Sample better

from plot_functions import replot
from scipy.optimize import curve_fit
from src import text
import pandas as pd
import numpy as np
import sys


def usage():
    print(f'''{sys.argv[0]} inputrefnoise INPUT [kwargs]
    fs=float        Set sample rate in Hz (default: 50e6)
    Ts=float        Set sample period in s, overrides fs (default: 1/fs)
    delay=float     Set delay before first sample (default: 0)
    y=str           Comparator signal (default: Column 1)
    var=str         Variable to compare against (default: Column 2)
    Uses the same plotting kwargs as replot''')


def gauss(x, H, A, x0, sigma):
    return H + A * np.exp(-((x - x0) ** 2) / (2 * sigma**2))


def align_num(num):
    string = str(num)

    if '-' in string:
        return string[:12] if len(string) >= 12 else string
    else:
        return ' ' + string[:11] if len(string) >= 11 else ' ' + string


def plot(df, kwargs):
    param = {
        'fs': 50e6,
        'Ts': None,
        'y': df.columns[1],
        'var': df.columns[2],
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
            hue = series[param['var']]
            if series['x'] >= time:
                samples.append(series[param['y']])
                time += param['Ts']

        d_fill = pd.concat([d_fill, pd.Series([hue, np.mean(samples)])],
                           axis=1,
                           ignore_index=True)

    pd_sampled = pd.DataFrame(d_fill.T.values,
                              columns=['x', param['y']]).iloc[1:, :]

    y = pd_sampled[param['y']][1:].values - pd_sampled[param['y']][0:-1].values
    x = pd_sampled['x'][0:-1].values
    x = x + (x[-1] - x[-2]) * 0.5

    try:
        parameters, covariance = curve_fit(
            gauss,
            x,
            y,
            maxfev=100000,
            bounds=np.array([[-np.inf, 0, -np.inf, 0],
                             [np.inf, np.inf, np.inf, np.inf]]))

        print(f'''Gaussian fit parameters:
sigma {align_num(parameters[3])}
   mu {align_num(parameters[2])}
    A {align_num(parameters[1])}
    H {align_num(parameters[0])}''')

    except Exception as e:
        text.error(f'Unable to fit Gaussian curve: {e}')

    kwargs = ['pt=scatter'] + kwargs + [f'y={param["y"]}']
    replot.plot(pd_sampled, kwargs)
