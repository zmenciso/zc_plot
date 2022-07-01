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
from datetime import datetime

# Globals

CWD = os.getcwd()
PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
FUNC_DIR = os.path.join(PROJ_DIR, 'plot_functions')
LOG_DIR = os.path.join(PROJ_DIR, 'logs')

try:
    VERSION = subprocess.check_output(['git', 'rev-parse', '--short',
                                       'HEAD']).decode('ascii').strip()
except Exception:
    VERSION = 'UNKNOWN'

# Import all plot functions
# TODO: Only import invoked function
for entry in os.scandir(FUNC_DIR):
    if entry.is_file() and os.path.splitext(entry)[-1] == '.py':
        exec(
            f'from {os.path.basename(FUNC_DIR)} import {os.path.splitext(os.path.basename(entry))[0]}'
        )

PLOT = None
INPUT = None
KWARGS = None
EXPORT = None
LOG = None
VERBOSE = False
SUMMARY = False
RAW = False
INTERACT = False

# Functions


def usage(exitcode):
    print(f'''{sys.argv[0]} [options] PLOT INPUT [kwargs]
    -h  --help      [PLOT]  Display this message or PLOT usage
    -k  --kwargs    FILE    Load additional external kwargs from FILE
    -x  --export    FILE    Exports the current kwargs to FILE
    -l  --log       FILE    Change default logfile name (or 'none' to disable)
    -i  --interact          View data ingest before setting kwargs
    -v  --verbose           Enable verbose output
    -s  --summary           Feed in summary data instead of a waveform
    -r  --raw               Feed in a raw .csv file instead of a waveform

List of available PLOTs:''')

    for func in os.scandir(FUNC_DIR):
        if func.is_file() and os.path.splitext(entry)[-1] == '.py':
            print(f'    {os.path.splitext(os.path.basename(func))[0]}')

    print('\nINPUT must be a valid CSV, e.g. `data/my_data.csv`.')

    sys.exit(exitcode)


def log(kwargs, df):
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    if LOG == 'none':
        return time
    elif LOG:
        filename = LOG
    else:
        filename = LOG_DIR + '/' + time + '.log'

    filename = filename.replace("\\", "/")

    try:
        fout = open(filename, 'a')
    except Exception as e:
        print(f'ERROR: Could not open logfile `{filename}` for writing ({e})',
              file=sys.stderr)
        return time

    if SUMMARY:
        ingest_type = 'Summary'
    elif RAW:
        ingest_type = 'Raw'
    else:
        ingest_type = 'Wave'

    fout.write(f'cadence_plot ver. {VERSION}\n')
    fout.write(f'Executed on {time.split("T")[0]} at {time.split("T")[1]}\n')
    fout.write('-' * 80 + '\n\n')

    fout.write(f'Input file: {INPUT}\n')
    fout.write(f'Plot function: {PLOT}\n')
    fout.write(f'''Arguments:
    Data ingest type: {ingest_type}
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
    # Create default directories
    if not os.path.isdir(os.path.join(PROJ_DIR, 'plots')):
        allow = tools.query('Default `plots` directory does not exist, create it?', 'yes')
        if allow:
            os.mkdir(os.path.join(PROJ_DIR, 'plots'))

    if not os.path.isdir(os.path.join(PROJ_DIR, 'logs')):
        allow = tools.query('Default `logs` directory does not exist, create it?', 'yes')
        if allow:
            os.mkdir(os.path.join(PROJ_DIR, 'logs'))

    # Parse command line options
    args = sys.argv[1:]

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            args.pop(0)
            if args and args[0] in ' '.join(os.listdir(FUNC_DIR)):
                eval(f'{args[0]}.usage()')
                sys.exit(0)
            else:
                usage(0)
        elif args[0] == '-v' or args[0] == '--verbose':
            VERBOSE = True
        elif args[0] == '-s' or args[0] == '--summary':
            SUMMARY = True
        elif args[0] == '-i' or args[0] == '--interact':
            INTERACT = True
        elif args[0] == '-r' or args[0] == '--raw':
            RAW = True
        elif args[0] == '-k' or args[0] == '--kwargs':
            KWARGS = args.pop(1)
        elif args[0] == '-x' or args[0] == '--export':
            EXPORT = args.pop(1)
        elif args[0] == '-l' or args[0] == '--log':
            LOG = args.pop(1)
        else:
            print('ERROR: Not a valid option `{args[0]}`\n', file=sys.stderr)
            usage(1)

        args.pop(0)

    # Missing arguments
    if len(args) < 2:
        print('ERROR: Not enough arguments\n', file=sys.stderr)
        usage(2)

    else:
        PLOT = args.pop(0)
        INPUT = args.pop(0)
        kwargs = args

    # Check plot function, input file, external kwargs
    if PLOT not in ' '.join(os.listdir(FUNC_DIR)):
        print(f'ERROR: {PLOT} is not a valid function', file=sys.stderr)
        sys.exit(101)
    if not os.path.isfile(INPUT):
        print(f'ERROR: Input `{INPUT}` is not a valid file', file=sys.stderr)
        sys.exit(102)
    if KWARGS and not os.path.isfile(KWARGS):
        print(f'ERROR: External kwargs `{KWARGS}` is not a valid file',
              file=sys.stderr)
        sys.exit(103)

    # Ingest data
    if SUMMARY:
        df = ingest.ingest_summary(INPUT)
    elif RAW:
        tools.check_filetype(INPUT)
        df = pd.read_csv(INPUT)
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
        print('Ingested data:')
        print(df)
        print('\n' + '-' * 30 + ' kwarg editor ' + '-' * 30)
        kwargs += tools.input_list()

    # Export kwargs
    if EXPORT:
        logging.export_kwargs(kwargs, EXPORT, VERSION)

    # Log and plot!
    time = log(kwargs, df)
    kwargs = [f'time={time}'] + kwargs
    eval(f'{PLOT}.plot(df, kwargs)')
    sys.exit(0)
