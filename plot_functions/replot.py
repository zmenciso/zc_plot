# Zephan M. Enciso
# Intelligent MicroSystems Lab

# from plot_functions import test
from src import tools
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import sys
import os


def usage():
    print(f'{sys.argv[0]} [options] replot INPUT [kwargs]')
    print('''
Data
    x=str                       Change x (default: first column)
    y=list                      Change y (default: second column)
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
    bbox=str        bb=str      Bbox pos (right/center/inside/none, default: 'right')
    xlim=tuple                  Change xlim (default: full range)
    ylim=tuple                  Change ylim (default: full range)
Drawing
    width=float     w=float     Change marker or line width (default: Depends)
    alpha=float     a=float     Change alpha (default: 0.5)
    palette=list    c=list      Palette, accepts cubehelix (default: 'crest')
    ptype=str       pt=str      Change the plot type (default: 'line')
    ci=float                    Change confidence interval size (default: 95)
    stat=str                    Change stat/estimator (default: Depends)
    bins=int                    Change number of bins/levels (default: 10)
    fill=bool                   Enable/disable fill (default: Depends)
    multiple=str                Change multiple behavior (default: 'layer')
File
    filetype=str    ft=str      Change filetype (default: 'svg')
    filename=str    fn=str      Custom filename

Spaces in expression/signal names are not supported!''')


def draw(y, df, cmap):
    if 'line' in param['ptype']:
        ax = sns.lineplot(data=df,
                          x=param['x'],
                          y=y,
                          hue=param['hue'],
                          style=param['style'],
                          size=param['size'],
                          alpha=param['alpha'],
                          estimator=param['stat'] if param['stat'] else 'mean',
                          lw=param['width'] if param['width'] else 2,
                          ci=param['ci'],
                          palette=cmap)

    if 'scatter' in param['ptype']:
        ax = sns.scatterplot(data=df,
                             x=param['x'],
                             y=y,
                             hue=param['hue'],
                             style=param['style'],
                             size=param['size'],
                             alpha=param['alpha'],
                             edgecolor=None,
                             s=param['width'] if param['width'] else 16,
                             palette=cmap)

    elif 'joint' in param['ptype']:
        ax = sns.jointplot(data=df,
                           x=param['x'],
                           y=y,
                           kind=re.sub('joint', '', param['ptype']),
                           height=param['figsize'][0],
                           hue=param['hue'],
                           palette=cmap)

    elif 'heat' in param['ptype']:
        # TODO: Rounding is cringe, remove it
        # TODO: Support for vmin, vmax
        if not param['hue'] or param['size'] or param['style']:
            print('ERROR: heamap must have only x, y, and hue defined',
                  file=sys.stderr)
        df[param['x']] = np.round(df[param['x']], 1)
        df[y] = np.round(df[y], 1)
        df = df.pivot_table(columns=param['x'], index=y, values=param['hue'])
        ax = sns.heatmap(data=df, cmap=cmap)

    if 'hist' in param['ptype']:
        ax = sns.histplot(data=df,
                          x=param['x'],
                          y=y if y != 'None' else None,
                          fill=not param['fill'],
                          stat=param['stat'] if param['stat'] else 'count',
                          bins=param['bins'],
                          hue=param['hue'],
                          kde=('kde' in param['ptype']),
                          multiple=param['multiple'],
                          cbar=True if y != 'None' else False,
                          cbar_kws=dict(shrink=.75) if y != 'None' else None,
                          palette=cmap)

    elif 'kde' in param['ptype']:
        ax = sns.kdeplot(data=df,
                         x=param['x'],
                         y=y if y != 'None' else None,
                         fill=param['fill'],
                         levels=param['bins'],
                         hue=param['hue'],
                         lw=param['width'] if param['width'] else 2,
                         multiple=param['multiple'],
                         cbar=True if y != 'None' else False,
                         cbar_kws=dict(shrink=.75) if y != 'None' else None,
                         palette=cmap)

    return ax


def draw_legend():
    if param['bbox'] == 'none' or 'heat' in param['ptype'] or not param['ltitle']:
        return

    handles, labels = plt.gca().get_legend_handles_labels()

    if len(param['y']) > 1:
        r = len(labels) // len(param['y'])
        for index, wave in enumerate(param['y']):
            for i in range(index * r, index * r + r):
                labels[i] = f'{wave} ' + labels[i]

    if param['bbox'] == 'center':
        plt.legend(handles,
                   labels,
                   loc='upper center',
                   bbox_to_anchor=(.5, 1.25),
                   ncol=len(handles),
                   title=param['ltitle']
                   if param['ltitle'].lower() != 'none' else None,
                   borderaxespad=0)

    else:
        plt.legend(handles,
                   labels,
                   loc='upper left' if param['bbox'] != 'inside' else None,
                   bbox_to_anchor=(1.02, 1) if param['bbox'] != 'inside' else None,
                   title=param['ltitle']
                   if param['ltitle'].lower() != 'none' else None,
                   borderaxespad=0)


def draw_labels(ax):
    # Label axes
    plt.xlabel(param['xlabel'])
    plt.ylabel(param['ylabel'])

    # Set axes limits
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

    return ax


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

    return conversion[key] if key in conversion else key


def augment_param():
    # Fix data types
    param['y'] = re.sub(r'\s+', '', param['y']).strip('{[()]}').split(',')
    param['palette'] = re.sub(r'\s+', '', param['palette']).strip('{[()]}').split(',')
    param['figsize'] = tuple(
        map(float, param['figsize'].strip('{[()]}').split(',')))
    param['alpha'] = float(param['alpha'])
    param['width'] = float(param['width']) if param['width'] else None
    param['ci'] = float(param['ci'])
    param['logy'] = param['logy'].lower() in ['t', 'true', 'yes', 'y', '1']
    param['logx'] = param['logx'].lower() in ['t', 'true', 'yes', 'y', '1']
    param['fill'] = bool(param['fill'])
    param['bins'] = int(param['bins'])
    param['xscale'] = float(param['xscale'])
    param['yscale'] = float(param['yscale'])
    param['hscale'] = float(param['hscale'])
    param['sscale'] = float(param['sscale'])
    param['ptype'] = param['ptype'].lower()

    # Set labels
    if not param['ylabel']:
        param['ylabel'] = param['y'][0]
    if not param['xlabel']:
        param['xlabel'] = param['x']

    # Set legend title
    if not param['ltitle'] and param['hue']:
        param['ltitle'] = f"{param['hue']}/{param['style']}" if param[
            'style'] else param['hue']
    elif not param['ltitle'] and len(param['y']) > 1:
        # TODO: Create legend for multiple y series without hue or style
        # param['ltitle'] = 'Series'
        param['ltitle'] = None

    return param


def rescale(df):
    if param['xscale'] != 1:
        df[param['x']] = df[param['x']] * param['xscale']
    if param['yscale'] != 1:
        df[param['y']] = df[param['y']] * param['yscale']
    if param['hscale'] != 1:
        df[param['hue']] = df[param['hue']] * param['hscale']
    if param['sscale'] != 1:
        df[param['size']] = df[param['size']] * param['sscale']

    return df


def plot(df, kwargs):
    global param
    param = {
        'figsize': '6,3',
        'alpha': 0.8,
        'logy': 'F',
        'logx': 'F',
        'bbox': 'right',
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
        'x': df.columns[0],
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
        try:
            key, value = arg.split('=')
            key = key_expander(key)
            param[key] = value
        except Exception as e:
            print(f'ERROR: Unable to decode arg {arg} ({e})', file=sys.stderr)

    # Fix param variable types
    param = augment_param()

    # Set figure size and type
    plt.figure(figsize=param['figsize'])
    sns.set_style(param['axes'])
    sns.set_context(param['context'])

    # Change hue column to floats
    if param['hue']:
        df[param['hue']] = df[param['hue']].astype(float)

    # Rescale (avoid multiplication duplication if possible)
    df = rescale(df)

    # Draw plots!
    for index, y in enumerate(param['y']):
        palette = param['palette'][index % len(param['palette'])]
        cmap = sns.color_palette(palette, as_cmap=True)
        ax = draw(y, df, cmap)

    ax = draw_labels(ax)
    draw_legend()
    plt.tight_layout()

    # Write out
    if param['filename']:
        filename = param['filename'] + '.' + param['filetype']
        allow = tools.query(f'Overwrite {filename}?', 'yes') if os.path.isfile(filename) else True
        if allow:
            plt.savefig(filename)
    else:
        y = re.sub('/', '-', '+'.join(param['y']))
        filename = f'./plots/{y}_' + f"{param['time']}.{param['filetype']}"
        plt.savefig(f'{filename}')

    print(f'Output:  {os.path.realpath(filename)}')
