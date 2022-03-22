#!/usr/bin/env python

# Zephan M. Enciso
# Intelligent MicroSystems Lab

import sys
import os
import re
import pandas as pd
import numpy as np

# Globals

SI = {
    'm': 'e-3',
    'u': 'e-6',
    'n': 'e-9',
    'p': 'e-12',
    'f': 'e-15',
    'a': 'e-18',
    'z': 'e-21',
    'k': 'e3',
    'M': 'e6',
    'G': 'e9',
    'T': 'e12',
    'P': 'e15',
    'E': 'e18'
}

PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
FUNC_DIR = PROJ_DIR + '/plot_functions'
CWD = os.getcwd()

for entry in os.scandir(FUNC_DIR):
    if entry.is_file() and os.path.splitext(entry)[-1] == '.py':
        exec(
            f'from {os.path.basename(FUNC_DIR)} import {os.path.splitext(os.path.basename(entry))[0]}'
        )

PLOT = None
INPUT = None
VERBOSE = False
SUMMARY = False
FILETYPE = 'svg'

# Functions


def usage(exitcode):
    print(f'''{sys.argv[0]} [OPTIONS] PLOT INPUT [kwargs]
    -h  --help      Display this message
    -v  --verbose   Enable verbose output
    -s  --summary   Feed in summary data instead of a waveform

PLOT is the plot you wish to create, defined in `plot_functions.py`:''')

    for func in os.scandir(FUNC_DIR):
        if func.is_file() and os.path.splitext(entry)[-1] == '.py':
            print(f'    {os.path.splitext(os.path.basename(func))[0]}')

    print('''
INPUT is the input data file, e.g. `data/my_data.csv`.
If no INPUT and no kwargs are given, prints the usage for the specified PLOT.'''
          )

    sys.exit(exitcode)


def ingest_wave(filename):
    if os.path.splitext(filename)[-1] != '.csv':
        print('ERROR: Input file must be .csv', file=sys.stderr)
        sys.exit(3)

    df_in = pd.read_csv(filename)
    df = pd.DataFrame()

    x = df_in.iloc[:, 0]
    for label, content in df_in.iloc[:, 1::2].iteritems():
        param = re.findall(r".+ \((.*)\) .+", label)[0].split(",")
        d_fill = pd.DataFrame(np.array(
            [x.astype(float), content.astype(float)]).T,
                              columns=['x', label.split()[0]])
        for term in param:
            d_fill[term.split('=')[0]] = np.repeat(float(term.split('=')[1]),
                                                   len(d_fill['x']))

        df = pd.concat([df, d_fill], axis=0, ignore_index=True)

    return df


def si_convert(df, columns):
    for col in df:
        repl = np.unique(df[col].str.extract(r'([a-zA-Z])'))

        for item in repl:
            df[col] = df[col].str.replace(item,
                                          SI[item],
                                          regex=False,
                                          case=True)

    df.columns = columns

    return df


def ingest_summary(filename):
    if os.path.splitext(filename)[-1] != '.csv':
        print('ERROR: Input file must be .csv', file=sys.stderr)
        sys.exit(3)

    df_in = pd.read_csv(filename)
    param = df_in.loc[df_in["Point"].str.contains("Parameters"), "Point"]

    df = pd.DataFrame(
        param.str.findall(r"[0-9a-z\.-]+=([0-9a-z\.-]+)").to_list(), )

    df = si_convert(df, re.findall(r"([0-9a-z\.-]+)=[0-9a-z\.-]+", param[0]))
    df = df.astype(float)
    outputs = df_in.loc[df_in["Point"] == "1", "Output"]

    for output in outputs:
        d_fill = pd.DataFrame(
            np.array(
                df_in[df_in["Output"] == output]["Nominal"].astype(float)).T,
            columns=[output],
        )
        df = pd.concat([df, d_fill], axis=1)

    return df


# Main execution

if __name__ == '__main__':
    # Parse command line options
    args = sys.argv[1:]

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            usage(0)
        elif args[0] == '-v' or args[0] == '--verbose':
            VERBOSE = True
        elif args[0] == '-s' or args[0] == '--summary':
            SUMMARY = True
        else:
            usage(1)

        args.pop(0)

    # No arguments
    if len(args) < 1:
        usage(2)

    # Specific PLOT usage
    elif len(args) == 1:
        PLOT = args.pop(0)
        eval(f'{PLOT}.usage()')
        sys.exit(0)

    # Normal
    else:
        PLOT = args.pop(0)
        INPUT = args.pop(0)
        kwargs = args

    if PLOT not in ' '.join(os.listdir(FUNC_DIR)):
        print(f'ERROR: {PLOT} is not a valid function', file=sys.stderr)
    if not os.path.isfile(INPUT):
        print(f'ERROR: {INPUT} does not exist', file=sys.stderr)

    if SUMMARY:
        df = ingest_summary(INPUT)
    else:
        df = ingest_wave(INPUT)

    eval(f'{PLOT}.plot(df, kwargs)')
    sys.exit(0)
