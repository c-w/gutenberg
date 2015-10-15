*********
Gutenberg
*********


Overview
========

This package contains a variety of scripts to make working with the `Project
Gutenberg <http://www.gutenberg.org>`_ body of public domain texts easier.

The functionality provided by this package includes:

* Downloading texts from Project Gutenberg.
* Cleaning the texts: removing all the crud, leaving just the text behind.
* Making meta-data about the texts easily accessible.

The package has been tested with Python 2.6, 2.7 and 3.4


Installation
============

This project is on `PyPI <https://pypi.python.org/pypi/Gutenberg>`_, so I'd
recommend that you just install everything from there using your favourite
Python package manager.

.. sourcecode :: sh

    pip install gutenberg

If you want to install from source or modify the package, you'll need to clone
this repository:

.. sourcecode :: sh

    git clone https://github.com/c-w/Gutenberg.git

Now, you should probably install the dependencies for the package and verify
your checkout by running the tests.

.. sourcecode :: sh

    cd Gutenberg

    virtualenv --no-site-packages virtualenv
    source virtualenv/bin/activate
    pip install -r requirements.pip

    pip install nose
    nosetests


Usage
=====

Downloading a text
------------------

.. sourcecode :: python

    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers

    text = strip_headers(load_etext(2701)).strip()
    print(text)  # prints 'MOBY DICK; OR THE WHALE\n\nBy Herman Melville ...'


Looking up meta-data
--------------------

.. sourcecode :: python

    from gutenberg.query import get_etexts
    from gutenberg.query import get_metadata

    print(get_metadata('title', 2701))  # prints 'Moby Dick; Or, The Whale'
    print(get_metadata('author', 2701)) # prints 'Melville, Hermann'

    print(get_etexts('title', 'Moby Dick; Or, The Whale'))  # prints (2701, ...)
    print(get_etexts('author', 'Melville, Hermann'))        # prints (2701, ...)


Note: The first time that one of the functions from `gutenberg.query` is called,
the library will create a rather large database of meta-data about the Project
Gutenberg texts. This one-off process will take quite a while to complete (18
hours on my machine) but once it is done, any subsequent calls to `get_etexts`
or `get_metadata` will be *very* fast.


Limitations
===========

This project *deliberately* does not include any natural language processing
functionality. Consuming and processing the text is the responsibility of the
client; this library merely focuses on offering a simple and easy to use
interface to the works in the Project Gutenberg corpus.  Any linguistic
processing can easily be done client-side e.g. using the `TextBlob
<http://textblob.readthedocs.org>`_ library.
