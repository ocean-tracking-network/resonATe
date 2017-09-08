# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='resonate',
    version='0.1.0',
    description='resonate data analysis package',
    long_description=readme,
    author='Alex Nunes',
    include_package_data=True,
    author_email='anunes@dal.ca',
    url='https://oceantrackingnetwork.org/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
