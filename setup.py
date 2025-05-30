# -*- coding: utf-8 -*-

from codecs import open

from setuptools import find_packages, setup

with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='resonATe',
    version='1.1',
    description='resonate data analysis package',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Jon Pye',
    include_package_data=True,
    author_email='jonpye@gmail.com',
    url='https://github.com/ocean-tracking-network/resonATe',
    download_url='https://github.com/ocean-tracking-network/resonATe',
    license='GPLv2',
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=('tests', 'docs'))
)
