import re
import os
import sys
from math import ceil
from src import tools


def usage():
    print(f'''{sys.argv[0]} [options] csv INPUT [kwargs]
    x=str                       First column for output (default: first column)
    y=list                      Columns to include (default: all other columns)
    points=int                  Number of data points (default: all)
    xscale=float    xs=float    Rescale x axis (default: 1)
    yscale=float    ys=float    Rescale y axis (default: 1)
    filename=str    fn=str      Output CSV file''')


def rescale(df):
    if param['xscale'] != 1:
        df[param['x']] = df[param['x']] * param['xscale']
    if param['yscale'] != 1:
        df[param['y']] = df[param['y']] * param['yscale']

    return df


def plot(df, kwargs):
    global param
    param = {
        'x': df.columns[0],
        'xscale': 1,
        'y': df.columns[1:],
        'yscale': 1,
        'points': None,
        'filename': None,
        'filetype': 'csv'
    }

    for arg in kwargs:
        key, value = arg.split('=')
        if key == 'fn':
            key = 'filename'
        elif key == 'xs':
            key = 'xscale'
        elif key == 'ys':
            key = 'yscale'

        param[key] = value

    param['y'] = re.sub(r'\s+', '', param['y']).strip('{[()]}').split(',') \
        if type(param['y']) == str \
        else list(param['y'])

    param['xscale'] = float(param['xscale'])
    param['yscale'] = float(param['yscale'])

    if param['points']:
        param['points'] = int(param['points'])
        n = ceil((len(df) - 1) / param['points'])
        df = df.iloc[::n, :].copy()

    df = rescale(df)

    param['y'].insert(0, param['x'])
    df_new = df[param['y']]

    if param['filename']:
        filename = param['filename'].strip('.csv') + '.' + param['filetype']
        allow = tools.query(f'Overwrite {filename}?', 'yes') \
            if os.path.isfile(filename) \
            else True
        if allow:
            df_new.to_csv(path_or_buf=filename, index=False)
    else:
        y = re.sub('/', '-', '+'.join(df_new.columns))
        filename = f'./plots/{y}_{param["time"]}.{param["filetype"]}'
        df_new.to_csv(path_or_buf=filename, index=False)

    print(f'Output: {os.path.realpath(filename)}')
