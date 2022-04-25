#!/usr/bin/env python

# Zephan M. Enciso
# Intelligent MicroSystems Lab

from datetime import datetime
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
    'E': 'e18',
    'nan': ''
}

PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
FUNC_DIR = PROJ_DIR + '/plot_functions'
CWD = os.getcwd()

LOG_DIR = CWD + '/logs'

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

# Functions


def usage(exitcode):
    print(f'''{sys.argv[0]} [OPTIONS] PLOT INPUT [kwargs]
    -h  --help      Display this message
    -k  [FILE]      Additional external kwargs (feed in from FILE)
    -x  [FILE]      Exports the current kwargs to FILE
    -v  --verbose   Enable verbose output
    -s  --summary   Feed in summary data instead of a waveform
    -r  --raw       Feed in a raw .csv file

PLOT is the plot you wish to create, defined in `plot_functions.py`:''')

    for func in os.scandir(FUNC_DIR):
        if func.is_file() and os.path.splitext(entry)[-1] == '.py':
            print(f'    {os.path.splitext(os.path.basename(func))[0]}')

    print('''
INPUT is the input data file, e.g. `data/my_data.csv`.
If no INPUT and no kwargs are given, prints the usage for the specified PLOT.'''
          )

    sys.exit(exitcode)


def query(prompt=None, default=None):
    '''Wait for user to input a y/n, with support for default'''

    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}

    if default is None:
        sel = ' [y/n] '
    elif default == 'yes':
        sel = ' [Y/n] '
    elif default == 'no':
        sel = ' [y/N] '
    else:
        raise ValueError(f'Invalid default answer: {default}')

    while True:
        response = input(prompt + sel)
        if (default is not None) and len(response) == 0:
            return valid[default]
        elif response.lower() in valid:
            return valid[response.lower()]


def log(kwargs, df):
    time = f'{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'
    if LOG:
        filename = LOG
    else:
        filename = LOG_DIR + '/' + time + '.log'

    try:
        fout = open(filename, 'a')
    except Exception as e:
        print(f'ERROR: Could not open logfile {filename} for writing ({e})',
              file=sys.stderr)
        return time

    if SUMMARY:
        ingest = 'Summary'
    elif RAW:
        ingest = 'Raw'
    else:
        ingest = 'Wave'

    fout.write('cadence_plot log file\n')
    fout.write(f'Executed at {time}\n')
    fout.write('-' * 80 + '\n\n')

    fout.write(f'Input file: {INPUT}\n')
    fout.write(f'Plot function: {PLOT}\n')
    fout.write(f'''Arguments:
    Verbose: {VERBOSE}
    Data ingest: {ingest}
    Export file: {EXPORT}
    External kwargs file: {KWARGS}\n''')

    fout.write('kwargs:\n')
    for kwarg in kwargs:
        fout.write(' ' * 4 + kwarg + '\n')

    # Dump DataFrame to fout
    fout.write('\n')
    print(df, file=fout)

    fout.close()
    return time


def export_kwargs(kwargs, filename):
    ''' TODO: Write this '''
    time = f'{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'

    try:
        fout = open(filename, 'w')
    except Exception as e:
        print(f'ERROR: Could not open export file {filename} for writing ({e})',
              file=sys.stderr)
        return

    fout.write('# cadence_plot kwargs file\n')
    fout.write(f'# Automatically generated at {time}\n')
    fout.write('#' * 80 + '\n\n')

    for kwarg in kwargs:
        try:
            fout.write(kwarg.split('=')[0] + '=' + kwarg.split('=')[1] + '\n')
        except Exception as e:
            print(f'ERROR: Misformed kwarg {kwarg} ({e})', file=sys.stderr)

    fout.close()
    return


def v_print(string, file):
    if VERBOSE:
        print(string, file=file)


def ingest_wave(filename):
    check_filetype(filename)

    df_in = pd.read_csv(filename)
    df = pd.DataFrame()

    x = df_in.iloc[:, 0]
    for label, content in df_in.iloc[:, 1::2].iteritems():
        param = list()
        if attr := re.findall(r".+ \((.*)\) .+", label):
            param = attr[0].split(",")

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
        repl = np.unique(df[col].str.extract(r'([a-zA-Z])').astype(str))

        for item in repl:
            df[col] = df[col].str.replace(item,
                                          SI[item],
                                          regex=False,
                                          case=True)

    df.columns = columns

    return df


def check_filetype(filename):
    if os.path.splitext(filename)[-1] != '.csv':
        print('ERROR: Input file must be .csv', file=sys.stderr)
        sys.exit(3)


def ingest_summary(filename):
    check_filetype(filename)

    df_in = pd.read_csv(filename)
    param = df_in.loc[df_in["Point"].str.contains("Parameters"), "Point"]

    df = pd.DataFrame(
        param.str.findall(r"[0-9a-z\.-]+=([0-9a-z\.-]*)").to_list(), )

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

    # Create default directories
    if not os.path.isdir(PROJ_DIR + '/plots'):
        allow = query('Default `plots` directory does not exist, create it?',
                      'yes')
        if allow:
            os.mkdir(PROJ_DIR + '/plots')
    if not os.path.isdir(PROJ_DIR + '/logs'):
        allow = query('Default `logs` directory does not exist, create it?',
                      'yes')
        if allow:
            os.mkdir(PROJ_DIR + '/logs')

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            usage(0)
        elif args[0] == '-v' or args[0] == '--verbose':
            VERBOSE = True
        elif args[0] == '-s' or args[0] == '--summary':
            SUMMARY = True
        elif args[0] == '-r' or args[0] == '--raw':
            RAW = True
        elif args[0] == '-k' or args[0] == '--kwargs':
            KWARGS = args.pop(1)
        elif args[0] == '-x' or args[0] == '--export':
            EXPORT = args.pop(1)
        elif args[0] == '-l' or args[0] == '--log':
            LOG = args.pop(1)
        else:
            usage(1)

        args.pop(0)

    # No arguments
    if len(args) < 1:
        usage(2)

    # PLOT usage function
    elif len(args) == 1:
        PLOT = args.pop(0)
        eval(f'{PLOT}.usage()')
        sys.exit(0)

    # Normal
    else:
        PLOT = args.pop(0)
        INPUT = args.pop(0)
        kwargs = args

    # Export kwargs
    if EXPORT:
        export_kwargs(kwargs, EXPORT)

    # Check plot function, input file
    if PLOT not in ' '.join(os.listdir(FUNC_DIR)):
        print(f'ERROR: {PLOT} is not a valid function', file=sys.stderr)
        sys.exit(101)
    if not os.path.isfile(INPUT):
        print(f'ERROR: {INPUT} is not a valid file', file=sys.stderr)
        sys.exit(102)

    # Ingest data
    if SUMMARY:
        df = ingest_summary(INPUT)
    elif RAW:
        check_filetype(INPUT)
        df = pd.read_csv(INPUT)
    else:
        df = ingest_wave(INPUT)

    # Concatenate kwargs with external kwargs
    if KWARGS:
        kwargs = [
            re.sub(r'\s+=\s+', '=', line.strip())
            for line in open(KWARGS) if line.strip() and not line.strip().startswith('#')
        ] + kwargs

    # Log and plot!
    time = log(kwargs, df)
    kwargs = [f'time={time}'] + kwargs
    eval(f'{PLOT}.plot(df, kwargs)')
    sys.exit(0)
