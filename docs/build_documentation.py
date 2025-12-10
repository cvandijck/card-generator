import shutil
import subprocess
import sys
from pathlib import Path


def main(args):
    doc_folder = Path(__file__).resolve().parent

    print('Build documentation using sphinx')
    try:
        print('Clean build folder')
        subprocess.run(['make.bat', 'clean'], cwd=doc_folder, universal_newlines=True, check=True, shell=True)

        if (doc_folder / 'api' / '_generated').is_dir():
            shutil.rmtree(doc_folder / 'api' / '_generated')

        print('Generate html documentation')
        subprocess.run(['make.bat', 'html'], cwd=doc_folder, universal_newlines=True, check=True, shell=True)

    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == '__main__':
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
