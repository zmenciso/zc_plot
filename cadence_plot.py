#!/usr/bin/env python

# Zephan M. Enciso
# Intelligent MicroSystems Lab

from datetime import datetime
import sys
import os
import re
import subprocess
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

CWD = os.getcwd()
PROJ_DIR = os.path.dirname(os.path.realpath(__file__))
FUNC_DIR = os.path.join(PROJ_DIR, 'plot_functions')
LOG_DIR = os.path.join(PROJ_DIR, 'logs')

try:
    VERSION = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
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
        ingest = 'Summary'
    elif RAW:
        ingest = 'Raw'
    else:
        ingest = 'Wave'

    fout.write(f'cadence_plot ver. {VERSION}\n')
    fout.write(f'Executed on {time.split("T")[0]} at {time.split("T")[1]}\n')
    fout.write('-' * 80 + '\n\n')

    fout.write(f'Input file: {INPUT}\n')
    fout.write(f'Plot function: {PLOT}\n')
    fout.write(f'''Arguments:
    Data ingest type: {ingest}
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


def export_kwargs(kwargs, filename):
    time = f'{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'

    allow = query(f'Overwrite {filename}?',
                  'yes') if os.path.isfile(filename) else True

    if not allow:
        return

    try:
        fout = open(filename, 'w')
    except Exception as e:
        print(
            f'ERROR: Could not open export file `{filename}` for writing ({e})',
            file=sys.stderr)
        return

    fout.write(f'# cadence_plot ver. {VERSION}\n')
    fout.write(
        f'# Automatically generated on {time.split("T")[0]} at {time.split("T")[1]}\n'
    )
    fout.write('#' * 80 + '\n\n')

    for kwarg in kwargs:
        try:
            fout.write(kwarg.split('=')[0] + '=' + kwarg.split('=')[1] + '\n')
        except Exception as e:
            print(f'ERROR: Misformed kwarg `{kwarg}` ({e})', file=sys.stderr)

    fout.close()
    return


def v_print(string, file=sys.stdout):
    if VERBOSE:
        print(string, file=file)


def ingest_wave(filename):
    check_filetype(filename)

    df_in = pd.read_csv(filename)
    x = df_in.iloc[:, 0]

    num = len(np.unique([item.split()[0] for item in df_in.columns]))
    df = pd.DataFrame(np.tile(np.array(x).astype(float), len(df_in.columns) // 2 // num).T, columns=['x'])

    for i in range(num):
        df_fill = pd.DataFrame()

        for label, content in df_in.iloc[:, (i*num + 1):(i*num + num):2].iteritems():
            wave = label.split()[0].strip('/')
            param = list()

            if attr := re.findall(r".+ \((.*)\) .+", label):
                param = attr[0].split(",")

            d_fill = pd.DataFrame(np.array(
                [content.astype(float)]).T,
                                  columns=[wave])
            for term in param:
                d_fill[term.split('=')[0]] = np.repeat(float(term.split('=')[1]),
                                                       len(d_fill[wave]))

            df_fill = pd.concat([df_fill, d_fill], axis=0, ignore_index=True)

        df = pd.concat([df, df_fill], axis=1)

    return df.loc[:, ~df.columns.duplicated()].copy()


def si_convert(df, columns):
    for col in df:
        repl = np.unique(df[col].str.extract(r'([a-zA-Z])').astype(str))

        for item in repl:
            df[col] = df[col].str.replace(item, SI[item], regex=False, case=True)

    df.columns = columns

    return df


def input_list():
    contents = list()

    while True:
        try:
            line = input()
            contents.append(re.sub(r'\s+=\s+', '=', line.strip()))
        except EOFError or KeyboardInterrupt:
            break

    return contents


def check_filetype(filename):
    if os.path.splitext(filename)[-1] != '.csv':
        print('ERROR: Input file must be .csv', file=sys.stderr)
        sys.exit(3)


def ingest_summary(filename):
    check_filetype(filename)

    df_in = pd.read_csv(filename)
    param = df_in.loc[df_in["Point"].str.contains("Parameters"), "Point"]

    df = pd.DataFrame(
        param.str.findall(r"[0-9a-z\.-]+=([0-9a-z\.-]*)").to_list())

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
    # Create default directories
    if not os.path.isdir(os.path.join(PROJ_DIR, 'plots')):
        allow = query('Default `plots` directory does not exist, create it?',
                      'yes')
        if allow:
            os.mkdir(os.path.join(PROJ_DIR, 'plots'))

    if not os.path.isdir(os.path.join(PROJ_DIR, 'logs')):
        allow = query('Default `logs` directory does not exist, create it?',
                      'yes')
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
        df = ingest_summary(INPUT)
    elif RAW:
        check_filetype(INPUT)
        df = pd.read_csv(INPUT)
    else:
        df = ingest_wave(INPUT)

    # Concatenate kwargs with external kwargs
    if KWARGS:
        kwargs = [
            re.sub(r'\s+=\s+', '=', line.strip()) for line in open(KWARGS)
            if line.strip() and not line.strip().startswith('#')
        ] + kwargs

    # Interactive mode
    if INTERACT:
        print('Ingested data:')
        print(df + '\n')
        print('-' * 30 + ' kwarg editor ' + '-' * 30)
        kwargs += input_list()

    # Export kwargs
    if EXPORT:
        export_kwargs(kwargs, EXPORT)

    # Log and plot!
    time = log(kwargs, df)
    kwargs = [f'time={time}'] + kwargs
    eval(f'{PLOT}.plot(df, kwargs)')
    sys.exit(0)
