# Zephan M. Enciso
# Intelligent MicroSystems Lab

from datetime import datetime
# from plot_functions import test
import matplotlib.pyplot as plt
import seaborn as sns
import re
import sys


def usage():
    print(f'{sys.argv[0]} replot [-s] INPUT [kwargs]')
    print('''
Data
    x=str                       Change x (default: first column)
    y=str                       Change y (default: second column)
    hue=str         h=str       Specify hue (WARNING default: None)
    style=str       s=str       Specify style (default: None)
    size=str                    Specify size (default: None)
    xscale=float    xs=float    Rescale x axis (default: 1)
    yscale=float    ys=float    Rescale y axis (default: 1)
    hscale=float    hs=float    Rescale hue (default: 1)
    sscale=float    ss=float    Rescale style (default: 1)
Figure
    figsize=tuple   fs=tuple    Change figsize (default: '6,3')
    xlabel=str      xl=str      Change x axis label (default: x)
    ylabel=str      yl=str      Change y axis label (default: y)
    ltitle=str      lt=str      Change legend title (default: automatic)
    axes=str        ax=str      Change axes style (default: 'whitegrid')
    context=str     cx=str      Scale plot elements (default: 'notebook')
    logx=bool       lx=bool     Enable/disable log for x-axis (default: False)
    logy=bool       ly=bool     Enable/disable log for y-axis (default: False)
    bbox=bool       bb=bool     Enable/disable bbox for legend (default: True)
    xlim=tuple                  Change xlim (default: full range)
    ylim=tuple                  Change ylim (default: full range)
Drawing
    width=float     w=float     Change marker or line width (default: Depends)
    alpha=float     a=float     Change alpha (default: 0.5)
    palette=str     c=str       Palette, accepts cubehelix (default: 'crest')
    ptype=str       pt=str      Change the plot type (default: 'line')
    ci=float                    Change confidence interval size (default: 95)
    stat=str                    Change stat/estimator (default: Depends)
    bins=int                    Change number of bins/levels (default: 10)
    fill=bool                   Enable/disable fill (default: Depends)
    multiple=str                Change multiple behavior (default: 'layer')
File
    filetype=str    ft=str      Change filetype (default: 'svg')
    filename=str    fn=str      Custom filename''')


def key_expander(key):
    conversion = {
        'h': 'hue',
        's': 'style',
        'a': 'alpha',
        'c': 'palette',
        'lx': 'logx',
        'ly': 'logy',
        'bb': 'bbox',
        'xl': 'xlabel',
        'yl': 'ylabel',
        'lt': 'ltitle',
        'pt': 'ptype',
        'ft': 'filetype',
        'fn': 'filename',
        'w': 'width',
        'fs': 'figsize',
        'ax': 'axes',
        'cx': 'context',
        'xs': 'xscale',
        'ys': 'yscale',
        'hs': 'hscale',
        'ss': 'sscale'
    }

    if key in conversion:
        return conversion[key]
    else:
        return key


def plot(df, kwargs):
    # TODO: Fix sig figs on legend!

    param = {
        'figsize': '6,3',
        'alpha': 0.8,
        'logy': False,
        'logx': False,
        'bbox': True,
        'filetype': 'svg',
        'filename': None,
        'ltitle': None,
        'xlabel': None,
        'ylabel': None,
        'xlim': None,
        'ylim': None,
        'axes': 'whitegrid',
        'context': 'notebook',
        'palette': 'crest',
        'x': 'x',
        'y': df.columns[1],
        'hue': None,
        'style': None,
        'size': None,
        'ptype': 'line',
        'width': None,
        'ci': 95,
        'bins': 10,
        'fill': False,
        'stat': None,
        'multiple': 'layer',
        'xscale': 1,
        'yscale': 1,
        'hscale': 1,
        'sscale': 1
    }

    # Read kwargs
    for arg in kwargs:
        key, value = arg.split('=')
        key = key_expander(key)
        if key in param:
            param[key] = value

    # Fix data types
    param['figsize'] = tuple(map(float, param['figsize'].strip('()').split(',')))
    param['alpha'] = float(param['alpha'])
    param['width'] = float(param['width']) if param['width'] else None
    param['ci'] = float(param['ci'])
    param['logy'] = bool(param['logy'])
    param['logx'] = bool(param['logx'])
    param['bbox'] = bool(param['bbox'])
    param['fill'] = bool(param['fill'])
    param['bins'] = int(param['bins'])
    param['xscale'] = float(param['xscale'])
    param['yscale'] = float(param['yscale'])
    param['hscale'] = float(param['hscale'])
    param['sscale'] = float(param['sscale'])

    # Set labels
    if not param['ylabel']:
        param['ylabel'] = param['y']
    if not param['xlabel']:
        param['xlabel'] = param['x']

    # Set legend title
    if not param['ltitle']:
        param['ltitle'] = f"{param['hue']}/{param['style']}" if param[
            'style'] else param['hue']

    plt.figure(figsize=param['figsize'])

    if param['hue']:
        df[param['hue']] = df[param['hue']].astype(float)

    cmap = sns.color_palette(param['palette'], as_cmap=True)

    sns.set_style(param['axes'])
    sns.set_context(param['context'])

    # Rescale
    if param['xscale'] != 1:
        df[param['x']] = df[param['x']] * param['xscale']
    if param['yscale'] != 1:
        df[param['y']] = df[param['y']] * param['yscale']
    if param['hscale'] != 1:
        df[param['hue']] = df[param['hue']] * param['hscale']
    if param['sscale'] != 1:
        df[param['size']] = df[param['size']] * param['sscale']

    # test.debug(param, df)

    # Draw plots
    if 'line' in param['ptype']:
        ax = sns.lineplot(data=df,
                          x=param['x'],
                          y=param['y'],
                          hue=param['hue'],
                          style=param['style'],
                          size=param['size'],
                          alpha=param['alpha'],
                          estimator=param['stat'] if param['stat'] else 'mean',
                          lw=param['width'] if param['width'] else 2,
                          ci=param['ci'],
                          palette=cmap)

    elif 'scatter' in param['ptype']:
        ax = sns.scatterplot(data=df,
                             x=param['x'],
                             y=param['y'],
                             hue=param['hue'],
                             style=param['style'],
                             size=param['size'],
                             alpha=param['alpha'],
                             edgecolor=None,
                             s=param['width'] if param['width'] else 16,
                             palette=cmap)

    elif 'hist' in param['ptype']:
        ax = sns.kdeplot(data=df,
                         x=param['x'],
                         y=param['y'] if param['y'] != 'None' else None,
                         fill=not param['fill'],
                         stat=param['stat'] if param['stat'] else 'count',
                         bins=param['bins'],
                         hue=param['hue'],
                         kde=('kde' in param['ptype']),
                         multiple=param['multiple'],
                         palette=cmap)

    elif 'kde' in param['ptype']:
        ax = sns.kdeplot(data=df,
                         x=param['x'],
                         y=param['y'] if param['y'] != 'None' else None,
                         fill=param['fill'],
                         levels=param['bins'],
                         hue=param['hue'],
                         lw=param['width'] if param['width'] else 2,
                         multiple=param['multiple'],
                         palette=cmap)

    plt.xlabel(param['xlabel'])
    plt.ylabel(param['ylabel'])

    if param['xlim']:
        param['xlim'] = tuple(map(float, param['xlim'].strip('()').split(',')))
        plt.xlim(param['xlim'])
    if param['ylim']:
        param['ylim'] = tuple(map(float, param['ylim'].strip('()').split(',')))
        plt.ylim(param['ylim'])

    if param['logx']:
        ax.set_xscale('log')
    if param['logy']:
        ax.set_yscale('log')

    if param['bbox'] and (param['hue'] or param['style']):
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles,
                   labels,
                   loc='upper left',
                   bbox_to_anchor=(1.02, 1),
                   title=param['ltitle'],
                   borderaxespad=0)

    plt.tight_layout()
    if param['filename']:
        plt.savefig(f'{param["filename"]}.{param["filetype"]}')
    else:
        param['y'] = re.sub('/', '-', param['y'])
        plt.savefig(
            f'{param["y"]}_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}.{param["filetype"]}'
        )
