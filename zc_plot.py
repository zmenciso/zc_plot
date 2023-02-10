#!/usr/bin/env python

# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

import sys
import os
import re
import subprocess
import pandas as pd
from src import ingest
from src import tools
from src import logging
from src import text
from datetime import datetime

# Globals

CWD = os.getcwd()
PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
FUNC_DIR = os.path.join(PROJ_DIR, 'plot_functions')
LOG_DIR = os.path.join(PROJ_DIR, 'logs')

try:
    VERSION = subprocess.check_output(['git', 'rev-parse', '--short',
                                       'HEAD']).decode('ascii').strip()
except Exception as e:
    VERSION = f'UNKNOWN ({e})'

PLOT = None
INPUT = None
KWARGS = None
EXPORT = None
LOG = None
VERBOSE = True
INTERACT = False
FILETYPE = 'wave'


# Functions

def log(kwargs, df):
    ''' Write logfile '''
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    if LOG == 'none':
        return time
    elif LOG:
        filename = LOG
    else:
        filename = os.path.join(LOG_DIR, f'{time}.log')

    try:
        fout = open(filename, 'a')
    except Exception as e:
        print(f'ERROR: Could not open logfile `{filename}` for writing ({e})',
              file=sys.stderr)
        return time

    fout.write(f'ZC Plot ver. {VERSION}\n')
    fout.write(f'Executed on {time.split("T")[0]} at {time.split("T")[1]}\n')
    fout.write('-' * 80 + '\n\n')

    fout.write(f'Input file: {INPUT}\n')
    fout.write(f'Plot function: {PLOT}\n')
    fout.write(f'''Arguments:
    Data ingest type: {FILETYPE.upper()}
    Verbose: {VERBOSE}
    Interactive: {INTERACT}
    Export file: {EXPORT}
    External kwargs file: {KWARGS}\n''')

    fout.write('kwargs:\n')
    for kwarg in kwargs:
        fout.write(' ' * 4 + kwarg + '\n')

    # Dump DataFrame to fout
    fout.write('\n')
    print(df, file=fout)

    fout.close()
    print(f'Logfile: {os.path.realpath(filename)}')
    return time


# Main execution

if __name__ == '__main__':
    # Parse command line options
    # TODO: Change this to argparse
    args = sys.argv[1:]

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            args.pop(0)
            if args and args[0] in ' '.join(os.listdir(FUNC_DIR)):
                exec(f'from {os.path.basename(FUNC_DIR)} import {args[0]}')
                eval(f'{args[0]}.usage()')
                sys.exit(0)
            else:
                text.usage(0, FUNC_DIR)
        elif args[0] == '-q' or args[0] == '--quiet':
            VERBOSE = False
        elif args[0] == '-v' or args[0] == '--version':
            print(f'Version {VERSION}') if VERSION else print('UNKNOWN VERSION')
            exit(0)
        elif args[0] == '-t' or args[0] == '--type':
            FILETYPE = args.pop(1).lower()
        elif args[0] == '-i' or args[0] == '--interact':
            INTERACT = True
        elif args[0] == '-k' or args[0] == '--kwargs':
            KWARGS = args.pop(1)
        elif args[0] == '-x' or args[0] == '--export':
            EXPORT = args.pop(1)
        elif args[0] == '-l' or args[0] == '--log':
            LOG = args.pop(1)
        else:
            print('ERROR: Not a valid option `{args[0]}`\n', file=sys.stderr)
            text.usage(1, FUNC_DIR)

        args.pop(0)

    # Missing arguments
    if len(args) < 2:
        print('ERROR: Not enough arguments\n', file=sys.stderr)
        text.usage(2, FUNC_DIR)

    else:
        PLOT = args.pop(0)
        INPUT = args.pop(0)
        kwargs = args

    # Create default directories
    if not os.path.isdir(os.path.join(PROJ_DIR, 'plots')):
        allow = tools.query('Default `plots` directory does not exist, create it?', 'yes')
        if allow:
            os.mkdir(os.path.join(PROJ_DIR, 'plots'))

    if not os.path.isdir(os.path.join(PROJ_DIR, 'logs')):
        allow = tools.query('Default `logs` directory does not exist, create it?', 'yes')
        if allow:
            os.mkdir(os.path.join(PROJ_DIR, 'logs'))

    # Check plot function, input file, external kwargs
    if not os.path.isfile(os.path.join(FUNC_DIR, f'{PLOT}.py')):
        print(f'ERROR: {PLOT} is not a valid function', file=sys.stderr)
        sys.exit(101)
    if not os.path.isfile(INPUT):
        print(f'ERROR: Input `{INPUT}` is not a valid file', file=sys.stderr)
        sys.exit(102)
    if KWARGS and not os.path.isfile(KWARGS):
        print(f'ERROR: External kwargs `{KWARGS}` is not a valid file', file=sys.stderr)
        sys.exit(103)

    # Ingest data
    if 'sum' in FILETYPE:
        df = ingest.ingest_summary(INPUT)
    elif 'raw' in FILETYPE:
        tools.check_filetype(INPUT)
        df = pd.read_csv(INPUT)
    elif 'mc' in FILETYPE or 'monte' in FILETYPE:
        df = ingest.ingest_wave_mc(INPUT)
    else:
        df = ingest.ingest_wave(INPUT)

    # Concatenate kwargs with external kwargs
    if KWARGS:
        kwargs = [
            re.sub(r'\s+=\s+', '=', line.strip()) for line in open(KWARGS)
            if line.strip() and not line.strip().startswith('#')
        ] + kwargs

    # Interactive mode
    if INTERACT:
        text.interactive_print(df, kwargs)
        kwargs += tools.input_list()

    # Export kwargs
    if EXPORT:
        logging.export_kwargs(kwargs, EXPORT, VERSION)

    # Import plot function
    exec(f'from {os.path.basename(FUNC_DIR)} import {PLOT}')

    # Log and plot!
    time = log(kwargs, df)
    kwargs = [f'time={time}', f'version={VERSION}'] + kwargs

    exec(f'from {os.path.basename(FUNC_DIR)} import {PLOT}')
    eval(f'{PLOT}.plot(df, kwargs)')
    sys.exit(0)
