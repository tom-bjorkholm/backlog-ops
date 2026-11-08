#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='backlogops',
  version='1.5.1',
  description='Library with backlog operations.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12',
  packages=['backlogops'],
  package_dir={'backlogops': 'src/backlogops'},
  package_data={'backlogops': ['src/py.typed']},
  install_requires=[
    'config-as-json >= 1.8',
    'cryptography >= 50.0.2',
    'jira[cli,opt] >= 3.10.5',
    'tableio >= 1.3',
    'tableio-cfg-json >= 2.0',
    'wizard-ui-bridge[textual] >= 1.5',
    'versionreporter >= 0.5',
    'edit-cfg-json >= 1.0.0',
  ]
)
