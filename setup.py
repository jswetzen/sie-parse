#!/usr/bin/python3
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
        packages = ['sys', 'pathlib', 'itertools', 'difflib', 'PySide', 'PySide.QtCore', 'PySide.QtGui'],
        excludes = []
        )

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('transformer_gui.py', base=base)
]

setup(name='Transformer_GUI',
      version = '1.0',
      description = 'Graphical accounting data transformer',
      options = dict(build_exe = buildOptions),
      executables = executables,
      requires=['PySide', 'cx_Freeze'])
