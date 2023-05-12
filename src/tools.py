#!/usr/bin/env python

# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

from src import text
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
        text.error('Input file must be .csv', 3)


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
        response = input('\033[93m' + prompt + sel + '\x1b[0m')
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


def preprocess(infile, outfile):
    check_filetype(infile)

    fin = open(infile)
    columns = fin.readline().split(',')

    index = re.search(r"([0:9])", columns[0]).group(0)
    count = 1
    labels = list()

    for col in columns:
        if (sig := re.search(r"([0-9]+)", col).group(1)) != index:
            index = sig
            count = 2
        else:
            count = count + 1

        labels.append(f"{col.split()[0]}-{count // 2} {col.split()[1]}")

    fout = open(outfile, 'w')
    fout.write(f'{",".join(labels)}\n')

    while line := fin.readline():
        fout.write(line)


