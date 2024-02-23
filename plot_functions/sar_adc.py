# Zephan M. Enciso
# Intelligent MicroSystems Lab

# This tool converts a series of comparator waveforms into ADC codes using peak
# detection.  It is especially useful for asynchronous SAR ADCs and expects a
# differential comparator (input a waveform representing COMP+ - COMP-).

import sys
import numpy as np
import pandas as pd
from src import text
from scipy import signal
from plot_functions import replot


def usage():
    print(f'{sys.argv[0]} [options] sar_adc INPUT [kwargs]')
    print('''
    time=str        Specify time signal (default: first column)
    comp=str        Specify comparator wave signal (default: second column)
    var=str         Specify swept variable (default: third column)
    prom=float      Change prominence for peak finding (default: 0.5)
    height=float    Change height for peak finding (default: prom)
    bits=int        Set number of bits (opt; performs sanity checks)
    tail=int        Display this number of the worst DNL (default: 0)''')


def plot(df, kwargs):
    param = {
        'time': df.columns[0],
        'comp': df.columns[1],
        'var': df.columns[2],
        'prom': 0.5,
        'height': None,
        'bits': 0,
        'tail': 0
    }

    # Parse kwargs
    for arg in kwargs:
        key, value = arg.split('=')
        param[key] = value

    param['prom'] = float(param['prom'])
    param['height'] = float(param['height']) if param['height'] else param['prom']
    param['inl'] = bool(param['inl'])
    param['dnl'] = bool(param['dnl'])
    param['tail'] = int(param['tail'])
    param['bits'] = int(param['bits'])

    codes = list()

    for var in np.unique(df[param['var']]):
        # Extract wave
        wave = df.loc[df[param['var']] == var, [param['comp']]].squeeze()

        # Find peaks
        pos = signal.find_peaks(wave,
                                prominence=param['prom'],
                                height=param['height'])
        neg = signal.find_peaks(wave * -1,
                                prominence=param['prom'],
                                height=param['height'])

        # Check bitwidth == number of peaks found
        if param['bits'] and len(pos[0]) + len(neg[0]) != param['bits']:
            text.error(f'Failed to decode {param["var"]} = {var} ({len(pos[0])}+ {len(neg[0])}-)')

        peaks = {key: "+" for key in pos[0]} | {key: "-" for key in neg[0]}

        # Convert into code
        code = 0
        for i, (time, sign) in enumerate(sorted(peaks.items())):
            if sign == "+":
                code = code + (2**(len(peaks) - 1 - i))

        codes.append((var, code))

    df_out = pd.DataFrame(np.array(codes), columns=[param['var'], 'code'])
    df_out['code'] = df_out['code'].astype(int)

    # Call replot
    replot.plot(df_out, kwargs)
