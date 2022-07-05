# Zephan M. Enciso
# Intelligent MicroSystems Lab

import sys
import re
import os
from src import tools


def usage():
    print(f'''{sys.argv[0]} [options] csv_dump INPUT [kwargs]
    x=str                       Rename column 'x' (wave ingest)
    filename=str    fn=str      Output CSV file''')


def plot(df, kwargs):
    param = {
        'x': None,
        'filename': None,
        'filetype': 'csv'
    }

    for arg in kwargs:
        key, value = arg.split('=')
        if key == 'fn':
            key = 'filename'

        param[key] = value

    if param['x']:
        df.rename(columns={'x': param['x']}, inplace=True)

    # Write out
    if param['filename']:
        filename = param['filename'].strip('.csv') + '.' + param['filetype']
        allow = tools.query(f'Overwrite {filename}?', 'yes') if os.path.isfile(filename) else True
        if allow:
            df.to_csv(path_or_buf=filename, index=False)
    else:
        y = re.sub('/', '-', '+'.join(df.columns[1:])) if not param['x'] else re.sub('/', '-', '+'.join(df.columns))
        filename = f'./plots/{y}_{param["time"]}.{param["filetype"]}'
        df.to_csv(path_or_buf=filename, index=False)

    print(f'Output:  {os.path.realpath(filename)}')
