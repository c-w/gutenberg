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
    return 0 < uid < 10


def _format_uri(uid):
    if _is_legacy_uid(uid):
        raise ValueError('should use legacy URI format for UIDs in (0..10)')

    uid = str(uid)
    return '{root}/{path}/{uid}/{uid}.txt'.format(
        root=r'http://www.gutenberg.lib.md.us',
        path='/'.join(uid[:len(uid) - 1]),
        uid=uid)


def _format_legacy_uri(uid):
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
