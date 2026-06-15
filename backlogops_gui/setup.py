#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='backlogops-gui',
  version='0.0.1',
  description='Graphical user interface for backlog operations.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12',
  packages=['backlogops_gui'],
  package_dir={'backlogops_gui': 'src/backlogops_gui'},
  package_data={'backlogops_gui': ['py.typed']},
  entry_points={
    'gui_scripts': [
      'backlogops-gui=backlogops_gui.application:main'
    ]
  },
  install_requires=[
    'backlogops >= 0.0.1',
    'argcomplete >= 3.6.3',
    'pip >= 26.1.1',
    'setuptools >= 82.0.1',
    'build >= 1.5.0',
    'wheel>=0.47.0'
  ]
)
