# Zephan M. Enciso
# Intelligent MicroSystems Lab

import pandas as pd
import numpy as np
import re
import sys
import os
from src import tools


def ingest_wave(filename):
    tools.check_filetype(filename)

    df_in = pd.read_csv(filename)
    x = df_in.iloc[:, 0]

    num = len(np.unique([item.split()[0] for item in df_in.columns]))
    series = len(df_in.columns) // 2 // num

    assert series

    df = pd.DataFrame(np.tile(np.array(x).astype(float), series).T,
                      columns=['x'])

    for i in range(num):
        df_fill = pd.DataFrame()

        for label, content in df_in.iloc[:, (2 * i * series + 1):(2 * i * series + 1 + (2 * series)):2].iteritems():
            wave = label.split()[0].strip('/')
            param = list()

            if attr := re.findall(r".+ \((.*)\) .+", label):
                param = attr[0].split(",")

            d_fill = pd.DataFrame(np.array([content.astype(float)]).T,
                                  columns=[wave])
            for term in param:
                d_fill[term.split('=')[0]] = np.repeat(
                    float(term.split('=')[1]), len(d_fill[wave]))

            df_fill = pd.concat([df_fill, d_fill], axis=0, ignore_index=True)

        df = pd.concat([df, df_fill], axis=1)

    return df.loc[:, ~df.columns.duplicated()].copy()


def ingest_summary(filename):
    tools.check_filetype(filename)

    df_in = pd.read_csv(filename)
    param = df_in.loc[df_in["Point"].str.contains("Parameters"), "Point"]

    df = pd.DataFrame(
        param.str.findall(r"[0-9a-z\.-]+=([0-9a-z\.-]*)").to_list())

    df = tools.si_convert(df, re.findall(r"([0-9a-z\.-]+)=[0-9a-z\.-]+", param[0]))
    df = df.astype(float)
    outputs = df_in.loc[df_in["Point"] == "1", "Output"]

    for output in outputs:
        d_fill = pd.DataFrame(
            np.array(
                df_in[df_in["Output"] == output]["Nominal"].astype(float)).T,
            columns=[output],
        )
        df = pd.concat([df, d_fill], axis=1)

    return df.dropna(axis=1, how='all')


def preprocess(infile, outfile):
    tools.check_filetype(infile)

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

def ingest_wave_mc(filename):
    temp_file = f'temp_{os.path.basename(filename)}'
    preprocess(filename, temp_file)

    df = ingest_wave(temp_file)

    try:
        os.remove(temp_file)
    except Exception as e:
        print(f'ERROR: Could not remove temporary file {temp_file} ({e})', file=sys.stderr)

    return df
