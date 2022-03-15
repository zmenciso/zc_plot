# Zephan M. Enciso
# Intelligent MicroSystems Lab

from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def usage():
    print('''replot INPUT [kwargs]
    y=str           Change y (default: second column)
    hue=str         Change hue (default: third column)
    style=str       Specify style (default: None)
    figsize=tuple   Change figsize (default: (18/3, 19/3))
    alpha=float     Change alpha (default: 0.5)
    logx=bool       Enable/disable log for x-axis (default: False)
    logy=bool       Enable/disable log for y-axis (default: False)
    bbox=bool       Enable/disable bbox for legend (default: True)
    filetype=str    Change filetype (default: svg)
    filename=str    Custom filename''')


def plot(df, kwargs):
    figsize = (18/3, 9/3)
    alpha = 0.5
    logy = False
    logx = False
    bbox = True
    filetype = 'svg'
    filename = None

    xlim = df['x'].iloc[-1]
    y = df.columns[1]
    hue = df.columns[2]
    style = None

    while kwargs:
        key, value = kwargs[0].split('=')

        if key == 'y':
            y = value
        elif key == 'hue':
            hue = value
        elif key == 'style':
            style = value
        elif key == 'size':
            figsize = value
        elif key == 'alpha':
            alpha = value
        elif key == 'logy':
            logy = bool(value)
        elif key == 'logx':
            logx = bool(value)
        elif key == 'filetype':
            filetype = value
        elif key == 'name':
            filename = value
        elif key == 'bbox':
            bbox = bool(value)

        kwargs.pop(0)

    sns.set_palette(sns.color_palette('viridis'))
    plt.figure(figsize=figsize)

    ax = sns.lineplot(data=df,
            x='x',
            y=y,
            hue=hue,
            style=style,
            alpha=alpha)

    plt.xlim(xlim)
    if logx:
        ax.set_xscale('log')
    if logy:
        ax.set_yscale('log')

    if bbox:
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles, labels, loc='upper left', bbox_to_anchor=(1.02, 1),
                title=hue, borderaxespad=0)

    plt.tight_layout()
    if filename:
        plt.savefig(f'{filename}.{filetype}')
    else:
        plt.savefig(f'{y}_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}.{filetype}')
