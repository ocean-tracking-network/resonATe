# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='otntoolbox',
    version='0.1.0',
    description='otn-toolbox data analysis package',
    long_description=readme,
    author='Alex Nunes',
    author_email='anunes@dal.ca',
    url='https://oceantrackingnetwork.org/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
