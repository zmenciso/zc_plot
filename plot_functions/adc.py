# Zephan M. Enciso
# Intelligent MicroSystems Lab

# This tool converts a series of comparator waveforms into ADC codes using peak
# detection.  It is especially useful for asynchronous SAR ADCs and expects a
# differential comparator (input a waveform representing COMP+ - COMP-).

import re
import sys
import numpy as np
import pandas as pd
from src import text
from plot_functions import replot


def usage():
    print(f'{sys.argv[0]} [options] sar_adc INPUT [kwargs]')
    print('''
    bits=int        Set number of bits (opt; performs sanity checks)
    dnl=bool        Enable DNL, requires var == code voltage (default: True)
    inl=bool        Enable INL, requires var == code voltage (default: False)
    var=str         Variable to plot against (default: Column 0)
    data=str        Label to check for bits (default: 'D')
    tail=int        Display this number of the worst DNL (default: 0)''')


def plot(df, kwargs):
    param = {
        'var': df.columns[0],
        'data': 'DATA',
        'bits': 0,
        'inl': False,
        'dnl': True,
        'tail': 0
    }

    # Parse kwargs
    for arg in kwargs:
        key, value = arg.split('=')
        param[key] = value

    param['inl'] = bool(param['inl'])
    param['dnl'] = bool(param['dnl'])
    param['tail'] = int(param['tail'])
    param['bits'] = int(param['bits'])

    df_out = pd.DataFrame(df[param['var']].copy())
    df_out = df_out.replace('0b', '', regex=False)
    df_out['code'] = np.zeros(len(df_out))

    for index, col in enumerate(df.columns[1:]):
        if param['data'] in col:
            i = re.match(r'.*([0-9]+).*', col)[1]
            df_out['code'] = df_out['code'] + (df[col] * (2 ** int(i)))

    if param['bits']:
        if (index + 1) != param['bits']:
            text.error(f'Decoded bitwidth ({index}) does not match specified bitwidth ({param["bits"]})', 123)

    if param['dnl']:
        df_out['dnl'] = np.append(
            np.array(df_out["code"][1:]) - np.array(df_out["code"][0:-1]),
            np.nan)
        df_out['abs_dnl'] = np.abs(df_out['dnl'])
        if param['tail']:
            print(
                df_out.sort_values("abs_dnl",
                                   ascending=False)[[param["var"],
                                                     "dnl"]][0:param['tail']])

    if param['inl'] and param['bits']:
        vmax = np.max(df[param['var']])
        vmin = np.min(df[param['var']])
        codespace = np.linspace(vmin, vmax, num=2**param['bits'])
        df_out['inl'] = [codespace[int(i)] for i in df_out["code"]]
    elif param['inl']:
        text.error('Bitwidth not specified; cannot compute INL')

    # Call replot
    replot.plot(df_out, kwargs)
