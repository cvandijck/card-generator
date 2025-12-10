# This pyinstaller hook file does not support ITK with `WrapITK.pth`.

from PyInstaller.utils.hooks import collect_data_files

# hiddenimports = ['new']

# If ITK is pip installed, gets all the files.
itk_datas = collect_data_files('itk', include_py_files=True)
datas = [x for x in itk_datas if '__pycache__' not in x[0]]

# make itk a dummy package to reduce size while avoid crash on not used import
# datas = [x for x in datas if not x[0].endswith('.dll')]
# datas = [x for x in datas if not x[0].endswith('.pyd')]
