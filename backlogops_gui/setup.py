#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='backlogops-gui',
  version='1.5',
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
    'backlogops >= 1.5',
    'argcomplete >= 3.7.2',
    'wizard-ui-bridge >= 1.5',
    'wizard-tk-bridge >= 1.5',
    'edit-cfg-json-tk >= 1.0.0',
    'versionreporter >= 0.5'
  ]
)
