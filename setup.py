from distutils.core import setup

setup(
    name='Gutenberg',
    version='0.1.1',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=['gutenberg', 'gutenberg.common'],
    scripts=[],
    url='https://bitbucket.org/c-w/gutenberg/',
    download_url='http://pypi.python.org/pypi/Gutenberg',
    license='LICENSE.txt',
    description='Project Gutenberg corpus interface',
    long_description=open('README.rst').read(),
    install_requires=list(line.strip() for line in open('requirements.txt')),
)
