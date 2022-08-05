# Zephan M. Enciso
# Intelligent MicroSystems Lab

import sys
import numpy as np
import pandas as pd
from scipy import signal
from plot_functions import replot


def usage():
    print(f'{sys.argv[0]} [options] replot INPUT [kwargs]')
    print('''
    time=str        Specify time signal (default: first column)
    comp=str        Specify comparator wave signal (default: second column)
    var=str         Specify swept variable (default: third column)
    prom=float      Change prominence for peak finding (default: 0.5)
    height=float    Change height for peak finding (default: prom)
    bits=int        Set number of bits (optional; performs sanity checks)''')


def plot(df, kwargs):
    param = {
        'time': df.columns[0],
        'comp': df.columns[1],
        'var': df.columns[2],
        'prom': 0.5,
        'height': None,
        'bits': None
    }

    # Parse kwargs
    for arg in kwargs:
        key, value = arg.split('=')
        param[key] = value

    param['prom'] = float(param['prom'])
    if not param['height']:
        param['height'] = param['prom']
    codes = list()

    for var in np.unique(df[param['var']]):
        # Extract wave
        wave = df.loc[df[param['var']] == var, [param['comp']]].squeeze()

        # Find peaks
        pos = signal.find_peaks(wave, prominence=param['prom'], height=param['height'])
        neg = signal.find_peaks(wave * -1, prominence=param['prom'], height=param['height'])

        # Check bitwidth == number of peaks found
        if param['bits'] and len(pos[0]) + len(neg[0]) != param['bits']:
            print(f'ERROR: Failed to decode wave ({len(pos[0])}+ {len(neg[0])}-)', file=sys.stderr)
            continue

        peaks = {key: "+" for key in pos[0]} | {key: "-" for key in neg[0]}

        # Convert into code
        code = 0
        for i, (time, sign) in enumerate(sorted(peaks.items())):
            if sign == "+":
                code = code + (2 ** (len(peaks) - 1 - i))

        codes.append((var, code))

    df_out = pd.DataFrame(np.array(codes), columns=[param['var'], 'code'])

    # Call replot
    kwargs.append(f'x={param["var"]}')
    replot.plot(df_out, kwargs)
