# Zephan M. Enciso
# zenciso@nd.edu
# Intelligent MicroSystems Lab

import os
import sys
from datetime import datetime
from src import tools
from src import text


def export_kwargs(kwargs, filename, version):
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    allow = tools.query(f'Overwrite {filename}?',
                        'yes') if os.path.isfile(filename) else True

    if not allow:
        return

    try:
        fout = open(filename, 'w')
    except Exception as e:
        text.error(f'Could not open file `{filename}` for writing ({e})')

    print(f'# ZC Plot ver. {version}', file=fout)
    print(
        f'# Automatically generated on {time.split("T")[0]} at {time.split("T")[1]}',
        file=fout
    )
    print('#' * 80 + '\n', file=fout)

    param = dict()
    for kwarg in kwargs:
        try:
            param[kwarg.split('=')[0]] = kwarg.split('=')[1]
        except Exception as e:
            text.error(f'Misformed kwarg `{kwarg}` ({e})')

    for key, value in param.items():
        print(f'{key} = {value}', file=fout)

    fout.close()

    text.cprint('OKBLUE', f'Export:  {os.path.realpath(filename)}')
    return
