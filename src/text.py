# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

import os
import sys
import re

banner = ''' _________   ____  _       _
|__  / ___| |  _ \\| | ___ | |_
  / / |     | |_) | |/ _ \\| __|
 / /| |___  |  __/| | (_) | |_
/____\\____| |_|   |_|\\___/ \\__|'''


def cprint(color, string, end='\n', file=sys.stdout):
    bcolors = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKCYAN': '\033[96m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    if color.upper() in bcolors:
        head = bcolors[color.upper()]
    else:
        head = f'\x1b[{color}m'

    tail = '\x1b[0m'

    print(head + string + tail, end=end, file=file)


def error(message, exitcode=None):
    cprint('1;91', f'ERROR: {message}', file=sys.stderr)

    if exitcode:
        sys.exit(exitcode)


def bar(header=None, char='#', length=os.get_terminal_size()[0]):
    ''' Return a bar with header centered in it '''
    output = '\n'

    if header:
        output += (length*char + '\n')
        output += (char + header.center(length-2) + char + '\n')

    output += (length*char + '\n')
    return output


def print_kwargs(kwargs):
    for kwarg in kwargs:
        print(re.sub('=', ' = ', kwarg))


def interactive_print(df, kwargs):
    print(banner)
    print(bar())
    print('Ingested data:')
    print(df)
    print(bar('Kwarg Editor'))
    print_kwargs(kwargs)


def usage(exitcode, func_dir):
    ''' Print usage to stdout '''
    print(banner)

    print(f'''
{sys.argv[0]} [options] PLOT INPUT [kwargs]
    -h  --help      [PLOT]  Display this message or usage for PLOT
    -k  --kwargs     FILE   Load additional external kwargs from FILE
    -x  --export     FILE   Exports the current kwargs to FILE
    -t  --type       TYPE   Input file type ('wave', 'summary', 'mc', or 'raw', default: 'wave')
    -l  --log        FILE   Logfile name (or 'none' to disable)
    -i  --interact          View data ingest before setting kwargs
    -q  --quiet             Surpress verbose output
    -v  --version           Print version string

List of available PLOTs:''')

    for func in os.scandir(func_dir):
        if func.is_file() and os.path.splitext(func)[-1] == '.py':
            print(f'    {os.path.splitext(os.path.basename(func))[0]}')

    print('\nINPUT must be a valid CSV, e.g. `data/my_data.csv`.')

    sys.exit(exitcode)
