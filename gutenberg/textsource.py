"""Module providing implementations of the api.TextSource interface."""


from __future__ import absolute_import
from . import beautify
from . import api
from .common import wget
import itertools
import logging
import os
import rdflib
import tarfile


def _is_legacy_uid(uid):
    """Helper function for `remote_uri_formatter`.

    Returns:
        bool: True if the UID should use the legacy URI format.

    """
    return 0 < uid < 10


def _format_uri(uid):
    """Helper function for `remote_uri_formatter`.

    Returns:
        str: The remote URI for the UID (in standard format).

    """
    if _is_legacy_uid(uid):
        raise ValueError('should use legacy URI format for UIDs in (0..10)')

    uid = str(uid)
    return '{root}/{path}/{uid}/{uid}.txt'.format(
        root=r'http://www.gutenberg.lib.md.us',
        path='/'.join(uid[:len(uid) - 1]),
        uid=uid)


def _format_legacy_uri(uid):
    """Helper function for `remote_uri_formatter`.

    Returns:
        str: The remote URI for the UID (in legacy format).

    """
    if not _is_legacy_uid(uid):
        raise ValueError('should use non-legacy URI format for UIDs >= 10')

    legacy_files = (
        'when11',
        'bill11',
        'jfk11',
        'getty11',
        'const11',
        'liber11',
        'mayfl11',
        'linc211',
        'linc111',
    )
    return '{root}/{path}/{name}.txt'.format(
        root=r'http://www.gutenberg.lib.md.us',
        path='etext90',
        name=legacy_files[uid - 1])


def remote_uri_formatter(uid):
    """Project Guttenberg has a number of different remote URI formats for its
    ETexts - the purpose of this function is to abstract away these details.

    Sample remote URI formats:
        - Most ETexts follow the following remote URI format: `x/y/.../xyz`
          where x,y,... are the first n-1 digits of the UID and xyz is the
          full UID.
        - Some ETexts follow a legacy URI format: `etext90/filename.txt` where
          filename is some specific file name.

    Arguments:
        uid (int): The UID of the text for which to return a URI formatter.

    Returns:
        function: The appropriate remote URI formatter for the given UID.

    """
    if _is_legacy_uid(uid):
        return _format_legacy_uri

    return _format_uri


class GutenbergEbooks(api.TextSource):
    """Implementation of api.TextSource that fetches books from Project
    Gutenberg.

    """
    RDF_URL = r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'

    def cleanup_text(self, lines):
        return beautify.strip_headers(lines)

    def _raw_source(self, start, stop, step):
        logging.info('fetching meta-data archive (this might take a while)')
        filename, _ = wget.grab(GutenbergEbooks.RDF_URL)
        with tarfile.open(filename) as archive:
            for tarinfo in itertools.islice(archive, start, stop, step):
                graph = rdflib.Graph()
                graph.parse(archive.extractfile(tarinfo))
                yield graph

    def _format_remote_uris(self, text_info):
        uri_formatter = remote_uri_formatter(text_info.uid)
        yield uri_formatter(text_info.uid)

    def textinfo_converter(self, rdf_graph):
        ebook = next(iter(rdf_graph.query('''
            SELECT
                ?ebook
                ?author
                ?title
            WHERE {
                ?ebook a pgterms:ebook.
                OPTIONAL { ?ebook dcterms:creator [ pgterms:name ?author ]. }
                OPTIONAL { ?ebook dcterms:title ?title. }
            }
            LIMIT 1
        ''')))
        return api.TextInfo(
            uid=int(os.path.basename(ebook.ebook.toPython())),
            author=ebook.author.toPython() if ebook.author else None,
            title=ebook.title.toPython() if ebook.title else None)
