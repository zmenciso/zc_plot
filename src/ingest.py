# Zephan M. Enciso
# Intelligent MicroSystems Lab

import pandas as pd
import numpy as np
import re
import os

from src.tools import preprocess, check_filetype, si_convert
from src.text import error


def ingest_wave(filename):
    check_filetype(filename)

    df_in = pd.read_csv(filename)
    x = df_in.iloc[:, 0]

    num = len(np.unique([item.split()[0] for item in df_in.columns]))
    series = len(df_in.columns) // 2 // num

    assert series

    df = pd.DataFrame(np.tile(np.array(x).astype(float), series).T,
                      columns=['x'])

    for i in range(num):
        df_fill = pd.DataFrame()

        for label, content in df_in.iloc[:, (2 * i * series + 1):(2 * i * series + 1 + (2 * series)):2].items():
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
    check_filetype(filename)

    df_in = pd.read_csv(filename)
    df_in = df_in.replace('eval err', 'NaN', regex=False)
    df_in = df_in.replace('0b', '', regex=False)
    param = df_in.loc[df_in["Point"].str.contains("Parameters"), "Point"]

    df = pd.DataFrame(
        param.str.findall(r"[0-9a-zA-Z\.-]+=([0-9a-zA-Z\.-]*)").to_list())

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

    return df.dropna(axis=1, how='all')


def ingest_wave_mc(filename):
    temp_file = f'temp_{os.path.basename(filename)}'
    preprocess(filename, temp_file)

    df = ingest_wave(temp_file)

    try:
        os.remove(temp_file)
    except Exception as e:
        error(f'Could not remove temporary file {temp_file} ({e})')

    return df
