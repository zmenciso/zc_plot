# Zephan M. Enciso
# Intelligent MicroSystems Lab

from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import sys


def usage():
    print('''replot INPUT [kwargs]
    y=str           Change y (default: second column)
    hue=str         Change hue (WARNING default: None)
    style=str       Specify style (default: None)
    figsize=tuple   Change figsize (default: 18/3,19/3)
    alpha=float     Change alpha (default: 0.5)
    logx=bool       Enable/disable log for x-axis (default: False)
    logy=bool       Enable/disable log for y-axis (default: False)
    bbox=bool       Enable/disable bbox for legend (default: True)
    xlabel=str      Change x axis label (default: 'x')
    ylabel=str      Change y axis label (default: y)
    xlim=tuple      Change xlim (default: full range)
    filetype=str    Change filetype (default: svg)
    filename=str    Custom filename''')


def plot(df, kwargs):
    figsize = (18 / 3, 9 / 3)
    alpha = 0.8
    logy = False
    logx = False
    bbox = True
    filetype = 'svg'
    filename = None
    xlabel = 'x'
    palette = None

    xlim = (df['x'].iloc[0], df['x'].iloc[-1])
    y = df.columns[1]
    hue = None
    style = None
    ylabel = y

    for arg in kwargs:
        key, value = arg.split('=')

        if key == 'y':
            y = value
        elif key == 'hue':
            hue = value
        elif key == 'style':
            style = value
        elif key == 'size':
            figsize = tuple(map(float, value.split(',')))
        elif key == 'alpha':
            alpha = float(value)
        elif key == 'logy':
            logy = bool(value)
        elif key == 'logx':
            logx = bool(value)
        elif key == 'filetype':
            filetype = value
        elif key == 'filename':
            filename = value
        elif key == 'bbox':
            bbox = bool(value)
        elif key == 'xlabel':
            xlabel = value
        elif key == 'ylabel':
            ylabel = value
        elif key == 'xlim':
            xlim = tuple(map(float, value.split(',')))
        else:
            print(f'ERROR: Unknown kwarg {key}', file=sys.stderr)

    if palette:
        sns.set_palette(sns.color_palette(palette))
    plt.figure(figsize=figsize)

    ax = sns.lineplot(data=df, x='x', y=y, hue=hue, style=style, alpha=alpha)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.xlim(xlim)
    if logx:
        ax.set_xscale('log')
    if logy:
        ax.set_yscale('log')

    if bbox and (hue or style):
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles,
                   labels,
                   loc='upper left',
                   bbox_to_anchor=(1.02, 1),
                   title=hue,
                   borderaxespad=0)

    plt.tight_layout()
    if filename:
        plt.savefig(f'{filename}.{filetype}')
    else:
        plt.savefig(
            f'{y}_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}.{filetype}')
