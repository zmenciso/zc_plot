# Zephan M. Enciso
# Intelligent MicroSystems Lab

from src import tools
from src import text

from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import sys
import os
import warnings


PARAM = {
    'figsize': '6.5,3',
    'alpha': 0.8,
    'logy': 'F',
    'logx': 'F',
    'logh': 'F',
    'bbox': 'right',
    'filetype': 'svg',
    'filename': None,
    'ltitle': None,
    'xlabel': None,
    'ylabel': None,
    'xlim': None,
    'ylim': None,
    'vlim': None,
    'axes': None,
    'context': 'notebook',
    'palette': 'crest',
    'x': 'x',
    'y': 'y',
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
    figsize=tuple   fs=tuple    Change figsize (default: '6.5,3')
    xlabel=str      xl=str      Change x axis label (default: x)
    ylabel=str      yl=str      Change y axis label (default: y)
    ltitle=str      lt=str      Change legend title (default: automatic)
    axes=str        ax=str      Change axes style (default: custom)
    context=str     cx=str      Scale plot elements (default: 'notebook')
    logx=bool       lx=bool     Enable/disable log for x-axis (default: False)
    logy=bool       ly=bool     Enable/disable log for y-axis (default: False)
    logh=bool                   Enable/disable log for hue / heatmap vlim (default: False)
    bbox=str        bb=str      Bbox pos (right/center/inside/none, default: 'right')
    xlim=tuple                  Change xlim (default: full range)
    ylim=tuple                  Change ylim (default: full range)
    vlim=tuple                  Change vlim (default: full range)
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
    warnings.filterwarnings("ignore")

    if 'joint' in PARAM['ptype']:
        ax = sns.jointplot(data=df,
                           x=PARAM['x'],
                           y=y,
                           kind=re.sub('joint', '', PARAM['ptype']),
                           height=PARAM['figsize'][0],
                           hue=PARAM['hue'],
                           hue_norm=LogNorm() if PARAM['logh'] else None,
                           palette=cmap,
                           marginal_ticks=True)

    elif 'scatter' in PARAM['ptype']:
        ax = sns.scatterplot(data=df,
                             x=PARAM['x'],
                             y=y,
                             hue=PARAM['hue'],
                             hue_norm=LogNorm() if PARAM['logh'] else None,
                             style=PARAM['style'],
                             size=PARAM['size'],
                             alpha=PARAM['alpha'],
                             edgecolor=None,
                             s=PARAM['width'] if PARAM['width'] else 16,
                             palette=cmap)

    if 'line' in PARAM['ptype']:
        ax = sns.lineplot(data=df,
                          x=PARAM['x'],
                          y=y,
                          hue=PARAM['hue'],
                          hue_norm=LogNorm() if PARAM['logh'] else None,
                          style=PARAM['style'],
                          size=PARAM['size'],
                          alpha=PARAM['alpha'],
                          estimator=PARAM['stat'] if PARAM['stat'] else 'mean',
                          lw=PARAM['width'] if PARAM['width'] else 2,
                          errorbar=('ci', PARAM['ci']),
                          palette=cmap)

    elif 'heat' in PARAM['ptype']:
        # TODO: Rounding is cringe, remove it
        if not PARAM['hue'] or PARAM['size'] or PARAM['style']:
            text.error('heatmap must have only x, y, and hue defined', 350)

        if PARAM['vlim']:
            PARAM['vlim'] = tuple(map(float, PARAM['vlim'].strip('()').split(',')))
        else:
            PARAM['vlim'] = (None, None)

        df[PARAM['x']] = np.round(df[PARAM['x']], 1)
        df[y] = np.round(df[y], 1)
        df = df.pivot_table(columns=PARAM['x'], index=y, values=PARAM['hue'])

        if PARAM['logh']:
            ax = sns.heatmap(data=df,
                             cmap=cmap,
                             robust=True,
                             annot=True,
                             norm=LogNorm() if PARAM['logh'] else None)
        else:
            ax = sns.heatmap(data=df,
                             cmap=cmap,
                             robust=True,
                             annot=True,
                             vmin=PARAM['vlim'][0],
                             vmax=PARAM['vlim'][1])

    if 'hist' in PARAM['ptype']:
        ax = sns.histplot(data=df,
                          x=PARAM['x'],
                          y=y if y.lower() != 'none' else None,
                          fill=not PARAM['fill'],
                          stat=PARAM['stat'] if PARAM['stat'] else 'count',
                          bins=PARAM['bins'],
                          hue=PARAM['hue'],
                          kde=('kde' in PARAM['ptype']),
                          multiple=PARAM['multiple'],
                          cbar=True if y.lower() != 'none' else False,
                          cbar_kws=dict(shrink=.75) if y.lower() != 'none' else None,
                          palette=cmap)

    elif 'kde' in PARAM['ptype']:
        ax = sns.kdeplot(data=df,
                         x=PARAM['x'],
                         y=y if y.lower() != 'none' else None,
                         fill=PARAM['fill'],
                         levels=PARAM['bins'],
                         hue=PARAM['hue'],
                         hue_norm=LogNorm() if PARAM['logh'] else None,
                         lw=PARAM['width'] if PARAM['width'] else 2,
                         multiple=PARAM['multiple'],
                         cbar=True if y != 'None' else False,
                         cbar_kws=dict(shrink=.75) if y != 'None' else None,
                         palette=cmap)

    return ax


def draw_legend():
    if PARAM['bbox'] == 'none' or 'heat' in PARAM['ptype'] or not PARAM['ltitle']:
        return

    handles, labels = plt.gca().get_legend_handles_labels()

    if len(PARAM['y']) > 1:
        r = len(labels) // len(PARAM['y'])
        for index, wave in enumerate(PARAM['y']):
            for i in range(index * r, index * r + r):
                labels[i] = f'{wave} ' + labels[i]

    if PARAM['bbox'] == 'center':
        plt.legend(handles,
                   labels,
                   loc='upper center',
                   bbox_to_anchor=(.5, 1.25),
                   ncol=len(handles),
                   title=PARAM['ltitle']
                   if PARAM['ltitle'].lower() != 'none' else None,
                   borderaxespad=0)

    else:
        plt.legend(handles,
                   labels,
                   loc='upper left' if PARAM['bbox'] != 'inside' else None,
                   bbox_to_anchor=(1.02, 1) if PARAM['bbox'] != 'inside' else None,
                   title=PARAM['ltitle']
                   if PARAM['ltitle'].lower() != 'none' else None,
                   borderaxespad=0)


def draw_labels(ax):
    # Label axes
    if PARAM['xlabel'].lower() == 'none':
        plt.xlabel(None)
    else:
        plt.xlabel(PARAM['xlabel'])

    if PARAM['ylabel'].lower() == 'none':
        plt.ylabel(None)
    else:
        plt.ylabel(PARAM['ylabel'])

    # Set axes limits
    if PARAM['xlim']:
        PARAM['xlim'] = tuple(map(float, PARAM['xlim'].strip('()').split(',')))
        plt.xlim(PARAM['xlim'])
    if PARAM['ylim']:
        PARAM['ylim'] = tuple(map(float, PARAM['ylim'].strip('()').split(',')))
        plt.ylim(PARAM['ylim'])
    if PARAM['logx']:
        ax.set_xscale('log')
    if PARAM['logy']:
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


def augment_PARAM():
    # Fix data types
    PARAM['y'] = re.sub(r'\s+', '', PARAM['y']).strip('{[()]}').split(',')
    PARAM['palette'] = re.sub(r'\s+', '', PARAM['palette']).strip('{[()]}').split(',')
    PARAM['figsize'] = tuple(
        map(float, PARAM['figsize'].strip('{[()]}').split(',')))
    PARAM['alpha'] = float(PARAM['alpha'])
    PARAM['width'] = float(PARAM['width']) if PARAM['width'] else None
    PARAM['ci'] = float(PARAM['ci'])
    PARAM['logy'] = PARAM['logy'].lower() in ['t', 'true', 'yes', 'y', '1']
    PARAM['logx'] = PARAM['logx'].lower() in ['t', 'true', 'yes', 'y', '1']
    PARAM['logh'] = PARAM['logh'].lower() in ['t', 'true', 'yes', 'y', '1']
    PARAM['fill'] = bool(PARAM['fill'])
    PARAM['bins'] = int(PARAM['bins'])
    PARAM['xscale'] = float(PARAM['xscale'])
    PARAM['yscale'] = float(PARAM['yscale'])
    PARAM['hscale'] = float(PARAM['hscale'])
    PARAM['sscale'] = float(PARAM['sscale'])
    PARAM['ptype'] = PARAM['ptype'].lower()

    if PARAM['ylim'] and 'none' in PARAM['ylim'].lower():
        PARAM['ylim'] = None
    if PARAM['xlim'] and 'none' in PARAM['xlim'].lower():
        PARAM['xlim'] = None
    if PARAM['vlim'] and 'none' in PARAM['vlim'].lower():
        PARAM['vlim'] = None

    # Set labels
    if not PARAM['ylabel']:
        PARAM['ylabel'] = PARAM['y'][0] \
            if 'hist' not in PARAM['ptype'] or 'kde' not in PARAM['ptype'] \
            else 'none'

    if not PARAM['xlabel']:
        PARAM['xlabel'] = PARAM['x']

    # Set legend title
    if not PARAM['ltitle'] and PARAM['hue']:
        PARAM['ltitle'] = f"{PARAM['hue']}/{PARAM['style']}" if PARAM[
            'style'] else PARAM['hue']
    elif not PARAM['ltitle'] and len(PARAM['y']) > 1:
        # TODO: Create legend for multiple y series without hue or style
        # PARAM['ltitle'] = 'Series'
        PARAM['ltitle'] = None

    return PARAM


def rescale(df):
    if PARAM['xscale'] != 1:
        df[PARAM['x']] = df[PARAM['x']] * PARAM['xscale']
    if PARAM['yscale'] != 1:
        df[PARAM['y']] = df[PARAM['y']] * PARAM['yscale']
    if PARAM['hscale'] != 1:
        df[PARAM['hue']] = df[PARAM['hue']] * PARAM['hscale']
    if PARAM['sscale'] != 1:
        df[PARAM['size']] = df[PARAM['size']] * PARAM['sscale']

    return df


def plot(df, kwargs):
    global PARAM
    PARAM['x'] = df.columns[0]
    PARAM['y'] = df.columns[1]

    # Read kwargs
    for arg in kwargs:
        try:
            key, value = arg.split('=')
            key = key_expander(key)
            PARAM[key] = value
        except Exception as e:
            text.error(f'Unable to decode arg {arg} ({e})')

    # Fix PARAM variable types
    PARAM = augment_PARAM()

    # Set figure size and type
    plt.figure(figsize=PARAM['figsize'])
    if not PARAM['axes']:
        sns.set_style('darkgrid', {'axes.facecolor': '#ebebeb'})
    else:
        sns.set_style(PARAM['axes'])
    sns.set_context(PARAM['context'])

    # Change hue column to floats
    if PARAM['hue']:
        df[PARAM['hue']] = df[PARAM['hue']].astype(float)

    # Rescale (avoid multiplication duplication if possible)
    df = rescale(df)

    # Draw plots!
    for index, y in enumerate(PARAM['y']):
        palette = PARAM['palette'][index % len(PARAM['palette'])]
        cmap = sns.color_palette(palette, as_cmap=True)
        ax = draw(y, df, cmap)

    ax = draw_labels(ax)
    # ax.set_xticklabels(np.array([f'{i:2.3f}' for i in plt.xticks()[0]]))
    draw_legend()
    plt.tight_layout()

    # Write out
    if PARAM['filename']:
        filename = PARAM['filename'] + '.' + PARAM['filetype']
    else:
        y = re.sub('/', '-', '+'.join(PARAM['y']))
        filename = f'./plots/{y}_' + f"{PARAM['time']}.{PARAM['filetype']}"

    allow = tools.query(f'Overwrite {filename}?', 'yes') \
        if os.path.isfile(filename) else True

    if allow:
        plt.savefig(filename)
        text.cprint('OKGREEN', f'Output:  {os.path.realpath(filename)}')
