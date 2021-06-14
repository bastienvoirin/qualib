from setuptools import setup

setup(
   name='qualib',
   version='0.1',
   description='Automatic calibrations for superconducting quantum circuits',
   author='Bastien Voirin',
   author_email='bastien.voirin@ens-lyon.org',
   url='https://github.com/bastienvoirin/qualib',
   packages=[
      'qualib'
   ],
   install_requires=[
      'numpy',
      'scipy',
      'nbformat'
   ],
   scripts=['qualib/main.py']
)
