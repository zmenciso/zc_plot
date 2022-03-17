# Zephan M. Enciso
# Intelligent MicroSystems Lab

from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import re


def usage():
    print('''replot [-s] INPUT [kwargs]
    x=str                       Change x (default: first column)
    y=str                       Change y (default: second column)
    hue=str         h=str       Change hue (WARNING default: None)
    style=str       s=str       Specify style (default: None)
    size=tuple                  Change figsize (default: '6,3')
    msize=float     ms=float    Change marker size for scatter (default: 10)
    alpha=float     a=float     Change alpha (default: 0.5)
    palette=str     c=str       Palette, accepts cubehelix (default: 'crest')
    logx=bool       lx=bool     Enable/disable log for x-axis (default: False)
    logy=bool       ly=bool     Enable/disable log for y-axis (default: False)
    bbox=bool       bb=bool     Enable/disable bbox for legend (default: True)
    xlabel=str      xl=str      Change x axis label (default: 'x')
    ylabel=str      yl=str      Change y axis label (default: y)
    ltitle=str      lt=str      Change legend title (default: automatic)
    xlim=tuple                  Change xlim (default: full range)
    ylim=tuple                  Change ylim (default: full range)
    ptype=str       pt=str      Change the plot type (default: 'line')
    axes=str        ax=str      Change axes style (default: 'whitegrid')
    context=str     cx=str      Scale plot elements (default: 'notebook')
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
        'ms': 'msize',
        'ax': 'axes',
        'cx': 'context'
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
        'xlabel': 'x',
        'xlim': None,
        'ylim': None,
        'axes': 'whitegrid',
        'context': 'notebook',
        'palette': 'crest',
        'x': 'x',
        'y': df.columns[1],
        'hue': None,
        'style': None,
        'ptype': 'line',
        'msize': 10
    }

    param['ylabel'] = param['y']

    for arg in kwargs:
        key, value = arg.split('=')
        key = key_expander(key)
        if key in param:
            param[key] = value

    param['figsize'] = tuple(map(float, param['figsize'].split(',')))
    param['alpha'] = float(param['alpha'])
    param['msize'] = float(param['msize'])
    param['logy'] = bool(param['logy'])
    param['logx'] = bool(param['logx'])
    param['bbox'] = bool(param['bbox'])

    if not param['ltitle']:
        param['ltitle'] = f"{param['hue']}/{param['style']}" if param[
            'style'] else param['hue']

    plt.figure(figsize=param['figsize'])

    if param['hue']:
        df[param['hue']] = df[param['hue']].astype(float)

    cmap = sns.color_palette(param['palette'], as_cmap=True)

    sns.set_style(param['axes'])
    sns.set_context(param['context'])

    if param['ptype'] == 'line':
        ax = sns.lineplot(data=df,
                          x=param['x'],
                          y=param['y'],
                          hue=param['hue'],
                          style=param['style'],
                          alpha=param['alpha'],
                          palette=cmap)
    elif param['ptype'] == 'scatter':
        ax = sns.scatterplot(data=df,
                             x=param['x'],
                             y=param['y'],
                             hue=param['hue'],
                             style=param['style'],
                             alpha=param['alpha'],
                             edgecolor=None,
                             s=param['msize'],
                             palette=cmap)

    plt.xlabel(param['xlabel'])
    plt.ylabel(param['ylabel'])

    if param['xlim']:
        param['xlim'] = tuple(map(float, param['xlim'].split(',')))
        plt.xlim(param['xlim'])
    if param['ylim']:
        param['ylim'] = tuple(map(float, param['ylim'].split(',')))
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
