#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages

setup(
    name='onlineparticipationdatasets',
    version='0.0.1',
    description='',
    url='https://github.com/Liebeck/OnlineParticipationDatasets',
    author='HHU Duesseldorf',
    author_email='liebeck@cs.uni-duesseldorf.de',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
    ]
)