"""Module to deal with metadata acquisition."""


from __future__ import absolute_import
import contextlib
import gzip
import logging
import os
import re
import shutil
import tarfile
import tempfile
import urllib2

from rdflib.graph import Graph
from rdflib.term import URIRef

from gutenberg._domain_model.persistence import local_path
from gutenberg._domain_model.vocabulary import DCTERMS
from gutenberg._domain_model.vocabulary import PGTERMS
from gutenberg._util.logging import disable_logging
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove


_METADATA_CACHE = local_path(os.path.join('metadata', 'metadata.rdf.nt.gz'))


@contextlib.contextmanager
def _download_metadata_archive():
    """Makes a remote call to the Project Gutenberg servers and downloads the
    entire Project Gutenberg meta-data catalog. The catalog describes the texts
    on Project Gutenberg in RDF. The function returns a file-pointer to the
    catalog.

    """
    data_url = r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'
    with tempfile.NamedTemporaryFile(delete=False) as metadata_archive:
        shutil.copyfileobj(urllib2.urlopen(data_url), metadata_archive)
    yield metadata_archive.name
    remove(metadata_archive.name)


def _iter_metadata_triples(metadata_archive_path):
    """Yields all meta-data of Project Gutenberg texts contained in the catalog
    dump.

    """
    is_invalid = lambda token: isinstance(token, URIRef) and ' ' in token
    with tarfile.open(metadata_archive_path) as metadata_archive:
        for item in metadata_archive:
            if re.match(r'^.*pg(?P<etextno>\d+).rdf$', item.name):
                with disable_logging():
                    graph = Graph().parse(metadata_archive.extractfile(item))
                for fact in graph:
                    if not any(is_invalid(token) for token in fact):
                        yield fact
                    else:
                        logging.info('skipping invalid triple %s', fact)


def _add_namespaces(graph):
    """Function to ensure that the graph always has some specific namespace
    aliases set.

    """
    graph.bind('pgterms', PGTERMS)
    graph.bind('dcterms', DCTERMS)
    return graph


def load_metadata(refresh_cache=False):
    """Returns a graph representing meta-data for all Project Gutenberg texts.
    Pertinent information about texts or about how texts relate to each other
    (e.g. shared authors, shared subjects) can be extracted using standard RDF
    processing techniques (e.g. SPARQL queries). After making an initial remote
    call to Project Gutenberg's servers, the meta-data is persisted locally.

    """
    metadata_graph = Graph()
    if refresh_cache:
        remove(_METADATA_CACHE)
    if not os.path.exists(_METADATA_CACHE):
        makedirs(os.path.dirname(_METADATA_CACHE))
        with _download_metadata_archive() as metadata_archive:
            for fact in _iter_metadata_triples(metadata_archive):
                metadata_graph.add(fact)
        with gzip.open(_METADATA_CACHE, 'wb') as metadata_file:
            metadata_file.write(metadata_graph.serialize(format='nt'))
    else:
        with gzip.open(_METADATA_CACHE, 'rb') as metadata_file:
            metadata_graph.parse(file=metadata_file, format='nt')
    return _add_namespaces(metadata_graph)
