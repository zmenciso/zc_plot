#!/usr/bin/env python

# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

import sys
import re
import os
import numpy as np

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


def check_filetype(filename):
    if os.path.splitext(filename)[-1] != '.csv':
        print('ERROR: Input file must be .csv', file=sys.stderr)
        sys.exit(3)


def si_convert(df, columns):
    for col in df:
        repl = np.unique(df[col].str.extract(r'([a-zA-Z])').astype(str))

        for item in repl:
            df[col] = df[col].str.replace(item, SI[item], regex=False, case=True)

    df.columns = columns

    return df


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


def input_list():
    contents = list()

    while True:
        try:
            line = input()
        except EOFError or KeyboardInterrupt:
            break

        if not line:
            break
        contents.append(re.sub(r'\s+=\s+', '=', line.strip()))

    return contents
