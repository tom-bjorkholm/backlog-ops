#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='backlogops',
  version='0.0.1',
  description='Library with backlog operations.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12',
  packages=['backlogops'],
  package_dir={'backlogops': 'src/backlogops'},
  package_data={'backlogops': ['src/py.typed']},
  install_requires=[
#    'argcomplete >= 3.6.3',
    'config-as-json >= 1.2',
    'tableio >= 1.0',
    'tableio-cfg-json >= 0.4',
    'versionreporter >= 0.2',
    'pip >= 26.1.1',
    'setuptools >= 82.0.1',
    'build >= 1.5.0',
    'wheel>=0.47.0'
  ]
)
