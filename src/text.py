# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

import os
import sys

banner = ''' _________   ____  _       _   
|__  / ___| |  _ \| | ___ | |_ 
  / / |     | |_) | |/ _ \| __|
 / /| |___  |  __/| | (_) | |_ 
/____\____| |_|   |_|\___/ \__|'''


def bar(header=None, length=80):
    output = '\n'

    if header:
        output += (length*'#' + '\n')
        output += ('#' + header.center(length-2) + '#\n')

    output += (length*'#' + '\n')
    return output


def interactive_print(df):
    print(banner)
    print(bar())
    print('Ingested data:')
    print(df)
    print(bar('Kwarg Editor'))


def usage(exitcode, func_dir):
    print(banner)

    print(f'''
{sys.argv[0]} [options] PLOT INPUT [kwargs]
    -h  --help      [PLOT]  Display this message or usage for PLOT
    -k  --kwargs     FILE   Load additional external kwargs from FILE
    -x  --export     FILE   Exports the current kwargs to FILE
    -l  --log        FILE   Change default logfile name (or 'none' to disable)
    -i  --interact          View data ingest before setting kwargs
    -q  --quiet             Surpress verbose output
    -v  --version           Print version string
    -s  --summary           Feed in summary data instead of a waveform
    -r  --raw               Feed in a raw .csv file instead of a waveform

List of available PLOTs:''')

    for func in os.scandir(func_dir):
        if func.is_file() and os.path.splitext(func)[-1] == '.py':
            print(f'    {os.path.splitext(os.path.basename(func))[0]}')

    print('\nINPUT must be a valid CSV, e.g. `data/my_data.csv`.')

    sys.exit(exitcode)
