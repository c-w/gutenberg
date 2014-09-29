from glob import glob
from distutils.core import setup

setup(
    name='Gutenberg',
    version='0.2.0',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=['gutenberg', 'gutenberg.common'],
    scripts=glob('scripts/*.py'),
    url='https://bitbucket.org/c-w/gutenberg/',
    download_url='http://pypi.python.org/pypi/Gutenberg',
    license='LICENSE.txt',
    description='Project Gutenberg corpus interface',
    long_description=open('README.rst').read(),
    install_requires=list(line.strip() for line in open('requirements.txt')),
)
