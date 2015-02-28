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
    assert text.startswith('MOBY DICK; OR THE WHALE\n\nBy Herman Melville')


Looking up meta-data
--------------------

.. sourcecode :: python

    from gutenberg.query import get_etexts
    from gutenberg.query import get_metadata

    assert get_metadata('title', 2701)  == 'Moby Dick; Or, The Whale'
    assert get_metadata('author', 2701) == 'Melville, Hermann'

    assert 2701 in get_etexts('title', 'Moby Dick; Or, The Whale')
    assert 2701 in get_etexts('author', 'Melville, Hermann')


Limitations
===========

This project *deliberately* does not include any natural language processing
functionality. Consuming and processing the text is the responsibility of the
client; this library merely focuses on offering a simple and easy to use
interface to the works in the Project Gutenberg corpus.  Any linguistic
processing can easily be done client-side e.g. using the `TextBlob
<http://textblob.readthedocs.org>`_ library.
