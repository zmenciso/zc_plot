#!/usr/bin/env python

# Zephan M. Enciso
# Intelligent MicroSystems Lab

import sys
import os
import pandas as pd
from plot_functions import *

# Globals

PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
FUNC_DIR = PROJ_DIR + '/plot_functions'
CWD = os.getcwd()

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

    for func in os.listdir(FUNC_DIR):
        print(f'    {os.path.splitext(func)[0]}')

    sys.exit(exitcode)


def ingest_wave(filename):
    if os.path.splitext(filename)[-1] != '.csv':
        print('ERROR: Input file must be .csv', file=sys.stderr)
        sys.exit(3)

    df = pd.read_csv(filename)

    return df


def ingest_summary(filename):
    pass


# Main execution

if __name__ == '__main__':
    # Parse command line options
    args = sys.argv[1:]

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            usage(0)
        elif args[0] == '-v' or args[0] == '--verbose':
            VERBOSE = True
        elif args[0] == '-f' or args[0] == '--filetype':
            FILETYPE = args.pop(1)
        else:
            usage(1)

        args.pop(0)

    if len(args) < 2:
        usage(2)
    else:
        PLOT = args.pop(0)
        INPUT = args.pop(0)
        kwargs = args

    if SUMMARY:
        df = ingest_summary(INPUT)
    else:
        df = ingest_wave(INPUT)

    eval(f'{PLOT}.plot(df, kwargs)')
