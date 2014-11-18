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

    git clone https://github.com/c-w/Gutenberg.git && cd Gutenberg

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


How to help
===========

* **(Good first fix)**
  Currently this library only makes use of the *author* and *title* meta-data
  exposed by Project Gutenberg and does not leverage information such as
  *genre*, *publication date*, etc. Making this information usable by the
  library is a pretty straight forward three-step process. First, the
  ``TextSource.textinfo_converter`` method needs to be extended to parse the new
  meta-data attributes. Second, the new attributes need to be wired through to
  the ``TextInfo`` class. Lastly, a new method leveraging the new meta-data
  source should be added to the ``Corpus`` class (such as ``texts_for_genre`` or
  ``texts_for_year``).
  See `#2 <https://github.com/c-w/Gutenberg/issues/2>`_.
* It would be great if there was an option to make the text retrieval functions
  on the ``Corpus`` class (like ``texts_for_author``) perform fuzzy matching so
  that small spelling mistakes can automatically be corrected.
  See `#3 <https://github.com/c-w/Gutenberg/issues/3>`_.
* The ``TextSource`` object should probably track its state so that it only
  yields every text once (unless explicitly requested to re-yield all texts from
  the start).
  See `#4 <https://github.com/c-w/Gutenberg/issues/4>`_.
* The library is in dire need of more tests and robustness fixes.
  See `#5 <https://github.com/c-w/Gutenberg/issues/5>`_.


Limitations
===========

This project *deliberately* does not include any natural language processing
functionality. Consuming and processing the text is the responsibility of the
client; this library merely focuses on offering a simple and easy to use
interface to the works in the Project Gutenberg corpus.  Any linguistic
processing can easily be done client-side e.g. using the `TextBlob
<http://textblob.readthedocs.org>`_ library.
