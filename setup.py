# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='openskyfetcher',
    version='0.1.0',
    description='openSkyFetcher',
    long_description=readme,
    author='erikson1970',
    author_email='erikson1970@users.noreply.github.com',
    url='https://github.com/Github account/openskyfetcher',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
    ]
)
