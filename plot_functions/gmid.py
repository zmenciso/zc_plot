# Zephan M. Enciso
# Intelligent MicroSystems Lab

from plot_functions import replot


def usage():
    print('''gmid INPUT [kwargs]
    REQUIRES SUMMARY INGEST
    gmid=str        Change gm/Id variable name (default: 'gm/Id')
    vgs=str         Change Vgs variable name (default: 'Vgs')
    id=str          Change Id variable name (default: 'Id')
    idwl=str        Change Id/(W/L) variable name (default: 'Id/(W/L)')
    vov=str         Change Vov variable name (default: 'Vov')
    ft=str          Change ft variable name (default: 'ft')
    Uses the same plotting kwargs as replot
    WARNING: Plots 3 figures, so changing filename will cause overwrite!''')


def plot(df, kwargs):
    param = {
            'gmid': 'gm/Id',
            'ft': 'ft',
            'vgs': 'Vgs',
            'id': 'Id',
            'idwl': 'Id/(W/L)',
            'vov': 'Vov'
            }

    for arg in kwargs:
        key, value = arg.split('=')
        if key in param:
            param[key] = value

    # Plot gm/Id vs Vov
    df['x'] = df[param['vov']]
    kwargs_gmid = kwargs + [f'y={param["gmid"]}', 'pt=scatter', 'xlabel=Vov [V]', 'ylabel=Gm/Id [1/V]']
    replot.plot(df, kwargs_gmid)

    # Plot Id/(W/L) vs gm/Id
    df['x'] = df[param['gmid']]
    kwargs_idwl = kwargs + [f'y={param["idwl"]}', 'pt=scatter', 'xlabel=Gm/Id [1/V]', 'ylabel=Id/(W/L) [A]']
    replot.plot(df, kwargs_idwl)

    # Plot ft vs gm/Id
    kwargs_ft = kwargs + [f'y={param["ft"]}', 'pt=scatter', 'xlabel=Gm/Id [1/V]', 'ylabel=ft [Hz]']
    replot.plot(df, kwargs_ft)
