#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='Blit',
      version=version,
      description='Simple pixel-composition library.',
      author='Michal Migurski',
      author_email='mike@stamen.com',
      requires=['NumPy','PIL'],
      packages=['Blit'],
      scripts=[],
      data_files=[],
      download_url='',
      license='BSD')
