# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='resonATe',
    version='0.2.2',
    description='resonate data analysis package',
    long_description=readme,
    author='Alex Nunes',
    include_package_data=True,
    author_email='anunes@dal.ca',
    url='https://gitlab.oceantrack.org/otndc/resonate',
    download_url = 'https://gitlab.oceantrack.org/otndc/resonate',
    license=license,
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=('tests', 'docs'))
)
