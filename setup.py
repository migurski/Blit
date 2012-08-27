#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='Blit',
      version=version,
      description='Simple pixel-composition library.',
      author='Michal Migurski',
      author_email='mike@stamen.com',
      url='https://github.com/migurski/Blit',
      requires=['numpy', 'sympy', 'PIL'],
      packages=['Blit'],
      scripts=[],
      data_files=[],
      download_url='https://github.com/downloads/migurski/Blit/Blit-%(version)s.tar.gz' % locals(),
      license='BSD')
