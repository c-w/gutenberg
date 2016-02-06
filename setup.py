"""Library installer."""

from os.path import isfile
from sys import version_info

from setuptools import find_packages
from setuptools import setup


def requirements_for(version=None):
    suffix = '-py%s' % version if version is not None else ''
    pip_path = 'requirements%s.pip' % suffix

    if not isfile(pip_path):
        return set()

    with open(pip_path) as pip_file:
        requirements = set(line.strip() for line in pip_file)
    return requirements


def install_requires():
    return requirements_for() | requirements_for(version_info.major)


setup(
    name='Gutenberg',
    version='0.4.2',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/c-w/Gutenberg',
    download_url='http://pypi.python.org/pypi/Gutenberg',
    license='LICENSE.txt',
    description='Library to interface with Project Gutenberg',
    long_description=open('README.rst').read(),
    install_requires=install_requires())
