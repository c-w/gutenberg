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

First of all, you should probably install the dependencies for the package and
verify your install.

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

Now that you're all set-up, let's get started. There are two ways to use this
project: from the command line and as a Python module.


From the command line
---------------------

The following functionality is available via the command line:

* Download some texts: ``python -m gutenberg.download``.
* Clean up a downloaded text: ``python -m gutenberg.beautify``.
* Grab some meta-data for the texts: ``python -m gutenberg.metainfo``.

For example, to download 10MB of texts to the directory *corpus*, you could run
the following:

.. sourcecode :: sh

    python -m gutenberg.download ./corpus --limit=10MB

You can find out more about how to run the scripts by appending *--help* to the
commands listed above.


As a module
-----------

You can also use the project as a Python package. The following snippet
demonstrates how you'd download some texts from Project Gutenberg and then
iterate over your freshly built corpus:

.. sourcecode :: python

    from gutenberg import GutenbergCorpus

    # this will setup the corpus and download 10MB worth of text to ./corpus
    corpus = GutenbergCorpus()
    corpus.download(limit=10 * 10**6)

    # iterate over the corpus
    preview_chars = 25
    for author in corpus.authors():
        for work in author.works():
            text = work.fulltext
            print(u'The first {preview_chars} characters of '
                   '"{title}" by "{author}" are:\n\t"{preview}"\n'
                   .format(preview_chars=preview_chars,
                           title=work.title,
                           author=author.name,
                           preview=text.replace('\n', ' ')[:preview_chars]))

You can also easily drill down on specific texts and authors:

.. sourcecode :: python

    shakespeare = corpus[u'Shakespeare, William']

    # list all the works for the author that we have currently available
    work_names = shakespeare.work_names()
    for work_num, title in enumerate(shakespeare.work_names(), start=1):
        print(u'Work {work_num} in the Shakespeare corpus: "{title}"'
              .format(work_num=work_num,
                      title=title))

    # inspect a particular text
    hamlet = shakespeare[u'Hamlet'].fulltext
    to_be_or_not_to_be = u'To be, or not to be, that is the Question'
    print(u'The famous quote "{quote}" is in Hamlet at position {position}.'
            .format(quote=to_be_or_not_to_be,
                    position=hamlet.find(to_be_or_not_to_be)))

All the loading of the heavy stuff is done lazily so you can just iterate over
authors and works at your heart's content without worrying about running out of
memory.


Advanced usage
==============

You can influence how the corpus object behaves via specifying a configuration
file when constructing the object:

.. sourcecode :: python

    corpus = GutenbergCorpus.using_config('my-corpus.cfg')

A configuration file can be generated from a corpus object like so:

.. sourcecode :: python

    corpus.write_config('path-to-config.cfg')

The default configuration looks like this:

.. sourcecode :: cfg

    [download]
    data_path = corpus/rawdata  # storage location of the raw Gutenberg texts
    offset = 0  # start downloading from this result page

    [database]
    database = corpus/gutenberg.db3  # storage location of the corpus DB
    drivername = sqlite  # the type of database to use for the corpus DB

    [metadata]
    metadata = corpus/metadata.json.gz  # storage location of the metadata DB

More information on the different configuration options can be found in the API
documentation of the *gutenberg.gutenberg* package.

The corpus database stores information about the downloaded texts. The database
has a single table, *etexts*, with four columns: *etextno*, *title*, *author*
and *path*. The first column is the primary key of the table and represents the
unique identifier of the work in the Project Gutenberg corpus.  The remaining
columns record meta-data about the work (in unicode) and a relative path to the
raw text on disk.


Limitations
===========

This project *deliberately* does not include any natural language processing
functionality. Consuming and processing the text is the responsibility of the
client; this library merely focuses on offering a simple and easy to use
interface to the works in the Project Gutenberg corpus.  Any linguistic
processing can easily be done client-side e.g. using the `TextBlob
<http://textblob.readthedocs.org>`_ library.
