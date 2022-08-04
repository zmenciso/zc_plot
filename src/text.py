# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

import os
import sys
import re

banner = ''' _________   ____  _       _   
|__  / ___| |  _ \| | ___ | |_ 
  / / |     | |_) | |/ _ \| __|
 / /| |___  |  __/| | (_) | |_ 
/____\____| |_|   |_|\___/ \__|'''


def bar(header=None, length=os.get_terminal_size()[0]):
    ''' Return a bar with header centered in it '''
    output = '\n'

    if header:
        output += (length*'#' + '\n')
        output += ('#' + header.center(length-2) + '#\n')

    output += (length*'#' + '\n')
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
    -l  --log        FILE   Change default logfile name (or 'none' to disable)
    -s  --summary           Feed in summary data instead of a waveform
    -r  --raw               Feed in a raw .csv file instead of a waveform
    -i  --interact          View data ingest before setting kwargs
    -q  --quiet             Surpress verbose output
    -v  --version           Print version string

List of available PLOTs:''')

    for func in os.scandir(func_dir):
        if func.is_file() and os.path.splitext(func)[-1] == '.py':
            print(f'    {os.path.splitext(os.path.basename(func))[0]}')

    print('\nINPUT must be a valid CSV, e.g. `data/my_data.csv`.')

    sys.exit(exitcode)
