#!/usr/bin/env python
import subprocess

import sys

import os
from setuptools import setup, find_packages, Command


class MypyCommand(Command):
  description = 'Run MyPy type checker'
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    """Run command."""
    command = ['mypy', '--strict', '--strict-optional', '--warn-return-any', '--warn-no-return', '--warn-unused-ignores', '--warn-redundant-casts', '--warn-incomplete-stub', '--check-untyped-defs', '--disallow-untyped-calls', '--disallow-untyped-defs', '--disallow-incomplete-defs', '--allow-subclassing-any', '--disallow-untyped-decorators', '--disallow-any-generics', '--no-implicit-optional', '--warn-unused-configs', 'cryfs', 'tests']
    myenv = os.environ.copy()
    myenv["MYPYPATH"] = "stubs/"
    returncode = subprocess.call(command, env=myenv)
    sys.exit(returncode)


dependencies = [
  'mypy == 0.560',
]

test_dependencies = [
  'nose == 1.3.7',
  'parameterized == 0.6.1',
  'coverage == 4.4.1',
  'asynctest == 0.10.0'
]

setup(name='cryfs-e2etest',
      version='0.1.0',
      description='Run end-to-end tests for the CryFS filesystem.',
      author='Sebastian Messmer',
      author_email='messmer@cryfs.org',
      license='GPLv3',
      url='https://github.com/cryfs/cryfs-e2etest',
      cmdclass={
        'mypy': MypyCommand,
      },
      packages=find_packages(),
      package_data = {
          'cryfs.e2etest.resources': [
              '*'
          ]
      },
      entry_points = {
        'console_scripts': [
          'cryfs-e2etest = cryfs.e2etest.__main__:main'
        ]
      },
      install_requires=dependencies,
      tests_require=test_dependencies,
      # For CI, we need to have a way of installing test dependencies.
      # Let's abuse extras_require for that.
      extras_require={
          'test': test_dependencies
      },
      test_suite='nose.collector',
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Filesystems",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities"
      ]
)
