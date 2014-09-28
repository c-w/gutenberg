*********
Gutenberg
*********


Overview
========

This package contains a variety of scripts to make working with the `Project
Gutenberg <http://www.gutenberg.org>`_ body of public domain texts easier.

The functionality provided by this package includes:

* Downloading texts using the Project Gutenberg API.
* Cleaning up the texts: removing headers and footers.
* Making meta-data about the texts easily accessible through a database.


Installation
============

This project is on `PyPI <https://pypi.python.org/pypi/Gutenberg>`_, so I'd
recommend that you just install everything from there using your favourite
Python package manager.

.. sourcecode :: sh

    pip install gutenberg
    easy_install gutenberg

If you want to install from source, you'll need to clone this repository:

.. sourcecode :: sh

    git clone https://c-w@bitbucket.org/c-w/gutenberg.git && cd gutenberg

Now, you should probably install the dependencies for the package and verify
your install.

* The recommended way of doing this is using the project's makefile. The
  command ``make virtualenv`` will install all the required dependencies for
  the package in a local directory called *virtualenv*
* You might want to run the tests to see if everything installed correctly:
  ``make test``.
* Now run ``source virtualenv/bin/activate`` and you're good to go.

Another setup task you might want to run is ``make docs`` to automatically
generate some API documentation for the project. After running the command, you
can enjoy your documentation by pointing your browser at
*docs/_build/html/index.html*.


Usage
=====

There are a number of programs demonstrating how to use this library in the
*scripts* directory.





Limitations
===========

This project *deliberately* does not include any natural language processing
functionality. Consuming and processing the text is the responsibility of the
client; this library merely focuses on offering a simple and easy to use
interface to the works in the Project Gutenberg corpus.  Any linguistic
processing can easily be done client-side e.g. using the `TextBlob
<http://textblob.readthedocs.org>`_ library.
