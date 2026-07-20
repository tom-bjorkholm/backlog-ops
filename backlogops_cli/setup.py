#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='backlogops-cli',
  version='0.4.1',
  description='Command line interface for backlog operations.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12',
  packages=['backlogops_cli'],
  package_dir={'backlogops_cli': 'src/backlogops_cli'},
  package_data={'backlogops_cli': ['src/py.typed']},
  install_requires=[
    'argcomplete >= 3.7.0',
    'backlogops >= 0.4.1',
    'versionreporter >= 0.4'
  ]
)
