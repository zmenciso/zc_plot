# Zephan M. Enciso
# Intelligent MicroSystems Lab

import pandas as pd
import numpy as np
import re
from src import tools


def ingest_wave(filename):
    tools.check_filetype(filename)

    df_in = pd.read_csv(filename)
    x = df_in.iloc[:, 0]

    num = len(np.unique([item.split()[0] for item in df_in.columns]))
    series = len(df_in.columns) // 2 // num
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
