from distutils.core import setup

setup(
    name='Gutenberg',
    version='0.1.0',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=['gutenberg', 'gutenberg.common'],
    scripts=[],
    url='http://pypi.python.org/pypi/Gutenberg',
    license='',
    description='Project Gutenberg corpus interface',
    long_description=open('ReadMe.md').read(),
    install_requires=list(line.strip() for line in open('requirements.txt')),
)
