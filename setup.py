"""Library installer."""

from __future__ import absolute_import, unicode_literals
from platform import system
from sys import version_info
import codecs

from setuptools import find_packages
from setuptools import setup


install_requires = [
    'future>=0.15.2',
    'rdflib>=4.2.0,<5.0.0',
    'requests>=2.5.1',
    'six>=1.10.0',
    'setuptools>=18.5',
    'rdflib-sqlalchemy>=0.3.8',
    'SPARQLWrapper>=1.8.2',
]

if version_info.major == 2:
    install_requires.extend([
        'functools32>=3.2.3-2',
    ])

if version_info.major == 3 or system() == 'Darwin':
    install_requires.extend([
        'bsddb3>=6.1.0',
    ])

with codecs.open('README.rst', encoding='utf-8') as fobj:
    long_description = fobj.read()

setup(
    name='Gutenberg',
    version='0.8.1',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/c-w/Gutenberg',
    download_url='https://pypi.python.org/pypi/Gutenberg',
    license='Apache Software License',
    description='Library to interface with Project Gutenberg',
    long_description=long_description,
    install_requires=sorted(install_requires),
    python_requires='>=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities'
    ])
