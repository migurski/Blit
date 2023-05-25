#!/usr/bin/env python

from setuptools import setup

version = open('VERSION', 'r').read().strip()

setup(name='Blit',
      version=version,
      description='Simple pixel-composition library.',
      author='Michal Migurski',
      author_email='mike@stamen.com',
      url='https://github.com/migurski/Blit',
      install_requires=['numpy', 'sympy', 'Pillow'],
      packages=['Blit'],
      scripts=[],
      data_files=[])
      # download_url='https://github.com/downloads/migurski/Blit/Blit-%(version)s.tar.gz' % locals(),
      #license='BSD')
