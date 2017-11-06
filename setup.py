# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='resonATe',
    version='0.1.7',
    description='resonate data analysis package',
    long_description=readme,
    author='Alex Nunes',
    include_package_data=True,
    author_email='anunes@dal.ca',
    url='https://gitlab.oceantrack.org/otndc/resonate',
    download_url = 'https://gitlab.oceantrack.org/otndc/resonate',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
