#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages

setup(
    name='onlineparticipationdatasets',
    version='1.1',
    description='',
    url='https://github.com/PGrawe/OnlineParticipationDatasets',
    install_requires=[
        'scrapy',
    ],
    packages=find_packages()
)
