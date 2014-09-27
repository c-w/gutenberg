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


class GutenbergEbooks(api.TextSource):
    """Implementation of api.TextSource that fetches books from Project
    Gutenberg.

    """
    RDF_URL = r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'

    def cleanup_text(self, lines):
        return beautify.strip_headers(lines)

    def _raw_source(self, start=0, stop=None, step=1):
        logging.info('fetching meta-data archive (this might take a while)')
        filename, _ = wget.grab(GutenbergEbooks.RDF_URL)
        with tarfile.open(filename) as archive:
            for tarinfo in itertools.islice(archive, start, stop, step):
                graph = rdflib.Graph()
                graph.parse(archive.extractfile(tarinfo))
                yield graph

    def _format_remote_uris(self, text_info):
        basic_url = '{root}/{path}/{uid}/{uid}.txt'.format(
            root=r'http://www.gutenberg.lib.md.us',
            path='/'.join(str(text_info.uid)[:4]),
            uid=text_info.uid)
        yield basic_url

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
