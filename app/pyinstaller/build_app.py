import os
import shutil
import subprocess
import sys
from pathlib import Path

from card_generator import _version
from card_generator.resources import get_resource_path

APP_NAME = f'Card_generator-{_version}'
APP_ICON = get_resource_path('card_generator.ico')
ADDITIONAL_DATA = [(get_resource_path(), 'data')]
ADDITIONAL_IMPORTS = []
ADDITIONAL_HOOKS = [Path(__file__).resolve().parent / 'hooks']
EXCLUDED_MODULES = ['jedi', 'tcl', 'FixTk', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'IPython', 'ipython', 'sphinx']


def main(args):
    pyinstaller_folder = Path(__file__).resolve().parent
    app_folder = pyinstaller_folder.parent
    root_folder = app_folder.parent

    dist_folder = pyinstaller_folder / '_dist'
    build_folder = pyinstaller_folder / '_build'

    print('Removing dist and build folders')
    shutil.rmtree(dist_folder, ignore_errors=True)
    shutil.rmtree(build_folder, ignore_errors=True)

    print('Build package')
    process = subprocess.run(
        ['python', '-m', 'build', f'--build-lib={build_folder}'], cwd=root_folder, text=True, check=True
    )

    print('Build app')
    # fmt: off
    pyinstaller_options = [
        '--noconfirm',
        '--name', APP_NAME,
        '--icon', str(APP_ICON),
        '--paths', str(build_folder),
        '--distpath', str(dist_folder),
        '--workpath', str(build_folder),
        '--specpath', str(build_folder)
    ]
    # fmt: on

    pyinstaller_options.extend([f'--add-data={src}{os.pathsep}{dest}' for src, dest in ADDITIONAL_DATA])
    pyinstaller_options.extend([f'--hidden-import={imp}' for imp in ADDITIONAL_IMPORTS])
    pyinstaller_options.extend([f'--additional-hooks-dir={hook}' for hook in ADDITIONAL_HOOKS])
    pyinstaller_options.extend([f'--exclude-module={excl}' for excl in EXCLUDED_MODULES])

    process = subprocess.run(['pyinstaller', 'app.py', *pyinstaller_options], cwd=app_folder, text=True)
    return process.returncode


if __name__ == '__main__':
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
