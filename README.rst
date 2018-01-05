*********
Gutenberg
*********

.. image:: https://travis-ci.org/c-w/gutenberg.svg?branch=master
    :target: https://travis-ci.org/c-w/gutenberg
.. image:: https://coveralls.io/repos/github/c-w/Gutenberg/badge.svg?branch=master
    :target: https://coveralls.io/github/c-w/Gutenberg?branch=master
.. image:: https://img.shields.io/pypi/v/gutenberg.svg
    :target: https://pypi.python.org/pypi/gutenberg/


Overview
========

This package contains a variety of scripts to make working with the `Project
Gutenberg <http://www.gutenberg.org>`_ body of public domain texts easier.

The functionality provided by this package includes:

* Downloading texts from Project Gutenberg.
* Cleaning the texts: removing all the crud, leaving just the text behind.
* Making meta-data about the texts easily accessible.

The package has been tested with Python 2.7, 3.4, 3.5 and 3.6.

An HTTP interface to this package exists too.
`Try it out! <https://github.com/c-w/gutenberg-http>`_


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


Python 3
--------

This package depends on BSD-DB. The bsddb module was removed from the Python
standard library since version 2.7. This means that if you wish to use gutenberg
on Python 3, you will need to manually install BSD-DB.

Linux
*****

On Linux, you can usually install BSD-DB using your distribution's package
manager. For example, on Ubuntu, you can use apt-get:

.. sourcecode :: sh

    sudo apt-get install libdb5.1-dev
    export BERKELEYDB_DIR=/usr
    pip install -r requirements-py3.pip

MacOS
*****

On Mac, you can install BSD-DB using `homebrew <https://homebrew.sh/>`_:

.. sourcecode :: sh

    brew install berkeley-db4
    pip install -r requirements-py3.pip

Windows
*******

On Windows, it's easiest to download a pre-compiled version of BSD-DB from
`pythonlibs <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_.

For example, if you have Python 3.5 on a 64-bit version of Windows, you
should download `bsddb3‑6.2.1‑cp35‑cp35m‑win_amd64.whl`.

After you download the wheel, install it and you're good to go:

.. sourcecode :: bash

    pip install bsddb3‑6.2.1‑cp35‑cp35m‑win_amd64.whl

License conflicts
*****************

Since its v6.x releases, BSD-DB switched to the `AGPL3 <https://www.gnu.org/licenses/agpl-3.0.en.html>`_
license which is stricter than this project's `Apache v2 <https://www.apache.org/licenses/LICENSE-2.0>`_
license. This means that unless you're happy to comply to the `terms <https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0)>`_
of the AGPL3 license, you'll have to install an ealier version of BSD-DB
(anything between 4.8.30 and 5.x should be fine). If you are happy to use this
project under AGPL3 (or if you have a commercial license for BSD-DB), set the
following environment variable before attempting to install BSD-DB:

.. sourcecode :: bash

    YES_I_HAVE_THE_RIGHT_TO_USE_THIS_BERKELEY_DB_VERSION=1


Usage
=====

Downloading a text
------------------

.. sourcecode :: python

    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers

    text = strip_headers(load_etext(2701)).strip()
    print(text)  # prints 'MOBY DICK; OR THE WHALE\n\nBy Herman Melville ...'

.. sourcecode :: sh

    python -m gutenberg.acquire.text 2701 moby-raw.txt
    python -m gutenberg.cleanup.strip_headers moby-raw.txt moby-clean.txt


Looking up meta-data
--------------------

A bunch of meta-data about ebooks can be queried:

.. sourcecode :: python

    from gutenberg.query import get_etexts
    from gutenberg.query import get_metadata

    print(get_metadata('title', 2701))  # prints frozenset([u'Moby Dick; Or, The Whale'])
    print(get_metadata('author', 2701)) # prints frozenset([u'Melville, Hermann'])

    print(get_etexts('title', 'Moby Dick; Or, The Whale'))  # prints frozenset([2701, ...])
    print(get_etexts('author', 'Melville, Hermann'))        # prints frozenset([2701, ...])

You can get a full list of the meta-data that can be queried by calling:

.. sourcecode :: python

    from gutenberg.query import list_supported_metadatas

    print(list_supported_metadatas()) # prints (u'author', u'formaturi', u'language', ...)

Before you use one of the `gutenberg.query` functions you must populate the
local metadata cache. This one-off process will take quite a while to complete
(18 hours on my machine) but once it is done, any subsequent calls to
`get_etexts` or `get_metadata` will be *very* fast. If you fail to populate the
cache, the calls will raise an exception.

To populate the cache:

.. sourcecode :: python

    from gutenberg.acquire import get_metadata_cache
    cache = get_metadata_cache()
    cache.populate()


If you need more fine-grained control over the cache (e.g. where it's stored or
which backend is used), you can use the `set_metadata_cache` function to switch
out the backend of the cache before you populate it. For example, to use the
Sqlite cache backend instead of the default Sleepycat backend and store the
cache at a custom location, you'd do the following:

.. sourcecode :: python

    from gutenberg.acquire import set_metadata_cache
    from gutenberg.acquire.metadata import SqliteMetadataCache

    cache = SqliteMetadataCache('/my/custom/location/cache.sqlite')
    cache.populate()
    set_metadata_cache(cache)


Limitations
===========

This project *deliberately* does not include any natural language processing
functionality. Consuming and processing the text is the responsibility of the
client; this library merely focuses on offering a simple and easy to use
interface to the works in the Project Gutenberg corpus.  Any linguistic
processing can easily be done client-side e.g. using the `TextBlob
<http://textblob.readthedocs.org>`_ library.
