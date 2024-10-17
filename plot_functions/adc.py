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
    dnl=bool        Enable DNL, requires var == code voltage, truncate output (default: False)
    inl=bool        Enable INL, requires var == code voltage, truncates output (default: False)
    var=str         Variable to calculate with, like code voltage (default: Column 0)
    data=str        Label to check for bits (default: 'D')
    tail=int        Display this number of the worst DNL and INL (default: 0)''')


def plot(df, kwargs):
    param = {
        'var': df.columns[0],
        'data': 'DATA',
        'bits': 0,
        'inl': False,
        'dnl': False,
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

    bits = [name for name in df.columns[1:] if (param['data'] in name)]

    for idx in bits:
        i = re.match(r'.*([0-9]+).*', idx)[1]
        df_out['code'] = df_out['code'] + (df[idx] * (2 ** int(i)))

    if param['bits'] and (len(bits) != param['bits']):
        text.error(f'Decoded bitwidth ({len(bits)}) does not match specified bitwidth ({param["bits"]})', 123)

    if param['dnl'] or param['inl']:
        df_out['diff'] = df_out['code'].diff()

        imax = df_out.iloc[::-1]['diff'].dropna().ne(0).idxmax() + 1
        imin = df_out['diff'].dropna().ne(0).idxmax()

        vmax = df_out.iloc[imax, :]['vdiff']
        vmin = df_out.iloc[imin, :]['vdiff']

        codespace = np.linspace(vmin, vmax, num=(2**len(bits) - 1))
        v_ideal = codespace[1] - codespace[0]

        steps = df_out.iloc[imin:imax, :].copy()
        steps = steps[steps['diff'].ne(0)]

        # Append missing codes
        for i in range(1, 2**len(bits)):
            if i not in steps['code'].values:
                n = i + 1
                while n not in steps['code'].values:
                    n = n + 1

                df_new = steps[steps['code'] == n].copy()
                df_new['code'] = i

                steps = pd.concat([steps, df_new])

        df_new = pd.DataFrame(np.array([range(1, 2**len(bits))]).T, columns=['code'])

        vd = [steps.loc[steps['code'] == i].iloc[0, 0] for i in range(1, 2**len(bits))]
        vd = np.array(vd)

        df_new['vd'] = vd

        if param['dnl']:
            df_new['vdp1'] = np.append(vd[1:], np.nan)

            df_new['dnl'] = ((df_new['vdp1'] - df_new['vd']) / v_ideal) - 1
            df_new['abs_dnl'] = np.abs(df_new['dnl'])

            if param['tail']:
                print(df_new.sort_values("abs_dnl", ascending=False)[['code', "dnl"]][0:param['tail']].to_string(index=False))

        if param['inl']:
            if param['dnl']:
                df_new['inl_sum'] = df_new['dnl'].cumsum()

            df_new['inl_cmp'] = (df_new['vd'] - pd.Series([codespace[int(i-1)] for i in df_new['code']])) / v_ideal

            df_new['inl'] = df_new['inl_cmp']

            df_new['abs_inl'] = np.abs(df_new['inl'])

            if param['tail']:
                print(df_new.sort_values("abs_inl", ascending=False)[['code', "inl"]][0:param['tail']].to_string(index=False))

        replot.plot(df_new, kwargs)

    else:
        # Call replot
        replot.plot(df_out, kwargs)
