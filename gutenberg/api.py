"""Defines the public interfaces of the gutenberg package."""


from __future__ import absolute_import
from .common import osutil
from .common import serialization
from .common import typesafe
from .common import wget
import abc
import gzip
import itertools
import logging
import os


class TextSource(serialization.SerializableObject):
    """Class to represent some external source of texts that can be fed into a
    corpus. The class handles conversion between the representations used in
    this API and the data found in the wild.
    For implementations of the class, refer to the gutenberg.textsource module.

    """
    __metaclass__ = abc.ABCMeta

    def __iter__(self):
        return iter(self.__getmany__(start=0, stop=None, step=1))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__getmany__(key.start, key.stop, key.step)
        elif isinstance(key, int):
            return self.__getsingle__(key)
        else:
            raise TypeError('Invalid argument type "%s"' % type(key))

    def __getmany__(self, start, stop, step):
        return itertools.imap(
            self.textinfo_converter,
            self._raw_source(start, stop, step))

    def __getsingle__(self, index):
        return next(self.__getmany__(start=index, stop=index + 1, step=1))

    @abc.abstractmethod
    def textinfo_converter(self, raw_instance):
        """Converts between the types that the TextSource implementation deals
        in and the API TextInfo type.

        Arguments:
            raw_instance (object): A raw-type instance of some text meta-data.

        Returns:
            TextInfo: The converted API-type text meta-data object.

        """
        raise NotImplementedError('abstract method')

    @abc.abstractmethod
    def _raw_source(self, start, stop, step):
        """Generates some meta-data in the format that the TextSource
        implementation deals in.

        Arguments:
            start (int): Slice offset.
            stop (int): Slice limit.
            step (int): Slice period.

        Yields:
            object: Raw-type instances of text meta-data.

        """
        raise NotImplementedError('abstract method')

    @abc.abstractmethod
    def _format_remote_uris(self, text_info):
        """Retrieves the candidate URIs at which some text could be located.

        Arguments:
            text_info (TextInfo): Meta-data about the text to be materialized.

        Yields:
            str: The candidate URIs at which the text could be located.

        """
        raise NotImplementedError('abstract method')

    @abc.abstractmethod
    def cleanup_text(self, lines):
        """Performs any necessary post-processing of a text.

        Arguments:
            lines (iter): An iterable over the lines in a text.

        Returns:
            list: Those lines in the text that are actual content.

        """
        raise NotImplementedError('abstract method')

    def fulltext(self, text_info):
        """Materializes a particular text from the TextSource by looking up the
        text's actual contents.

        Arguments:
            text_info (TextInfo): Meta-data about the text to be materialized.

        Returns:
            unicode: The full body of the text.

        """
        for uri in self._format_remote_uris(text_info):
            lines, success = wget.iter_lines(uri)
            if success:
                break
        else:
            logging.error('unable to fetch fulltext for %s', text_info)
            return u''

        return u'\n'.join(self.cleanup_text(lines))


class TextInfo(typesafe.namedtuple(
        'TextInfo',
        (('uid', int),
         ('title', unicode),
         ('author', unicode))
)):  # pylint: disable=R0903
    """Class to represent meta-data about a text.

    Attributes:
        uid (int): A unique identifier of the text.
        title (unicode): The title of the text.
        author (unicode): The author of the text.

    """
    pass


class Text(typesafe.namedtuple(
        'Text',
        (('location', str),
         ('fulltext', unicode),
         ('textinfo', TextInfo))
)):  # pylint: disable=R0903
    """Class to represent a text.

    Attributes:
        location (str): The on-disk location of the text.
        fulltext (unicode): The full text of the text.
        textinfo (TextInfo): Meta-data about the text.

    """
    pass


class Corpus(serialization.SerializableObject):
    """Class to represent a corpus i.e. a collection of texts and associated
    meta-data: authors, titles, etc.
    For implementations of the class, refer to the gutenberg.corpus module.

    Attributes:
        text_source (TextSource): The object that feeds the corpus with texts.
        basedir (str): The path to the corpus' serialization directory.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, text_source, basedir):
        self.text_source = text_source
        self.basedir = osutil.makedirs(basedir)
        self._textdir = osutil.makedirs(os.path.join(basedir, 'texts'))

    def _location(self, text_info):
        """This function is a one-to-one mapping between the TextInfo space and
        paths on the file-system that belong to the Corpus object (i.e.
        subpaths of Corpus.basedir).

        Arguments:
            TextInfo: The descriptor of the text to read/write

        Returns:
            str: A unique location at which the text can be read/written

        """
        return os.path.join(self._textdir, '%s.gz' % text_info.uid)

    def _fulltext(self, text_info):
        """Wrapper around TextSource.fulltext that caches texts on disk.

        Arguments:
            text_info (TextInfo): Meta-data about the text to be materialized.

        Returns:
            unicode: The full body of the text.

        """
        location = self._location(text_info)

        try:
            with gzip.open(location, 'rb') as gzipped:
                fulltext = gzipped.read()
        except IOError:
            fulltext = self.text_source.fulltext(text_info)
            if fulltext:
                with gzip.open(location, 'wb') as gzipped:
                    gzipped.write(fulltext)
        return fulltext

    @abc.abstractmethod
    def texts_for_author(self, author):
        """Retrieves all the texts from a given author from the corpus.

        Arguments:
            author (unicode): The author whose texts to retrieve.

        Yields:
            Text: The texts of the author, one at a time.

        """
        raise NotImplementedError('abstract method')
