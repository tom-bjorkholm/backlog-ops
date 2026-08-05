#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='backlogops',
  version='0.7.1',
  description='Library with backlog operations.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12',
  packages=['backlogops'],
  package_dir={'backlogops': 'src/backlogops'},
  package_data={'backlogops': ['src/py.typed']},
  install_requires=[
    'config-as-json >= 1.4',
    'cryptography >= 50.0.0',
    'jira[cli,opt] >= 3.10.5',
    'tableio >= 1.1',
    'tableio-cfg-json >= 1.2',
    'wizard-ui-bridge[textual] >= 1.2',
    'versionreporter >= 0.4'
  ]
)
