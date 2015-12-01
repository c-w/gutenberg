"""Library installer."""


from setuptools import find_packages
from setuptools import setup


setup(
    name='Gutenberg',
    version='0.4.1',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/c-w/Gutenberg',
    download_url='http://pypi.python.org/pypi/Gutenberg',
    license='LICENSE.txt',
    description='Library to interface with Project Gutenberg',
    long_description=open('README.rst').read(),
    install_requires=list(line.strip() for line in open('requirements.pip')))
