"""Module to deal with metadata acquisition."""
# pylint:disable=W0603


from __future__ import absolute_import
import contextlib
import logging
import os
import re
import shutil
import tarfile
import tempfile
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from rdflib.graph import Graph
from rdflib.term import URIRef

from gutenberg._domain_model.persistence import local_path
from gutenberg._domain_model.vocabulary import DCTERMS
from gutenberg._domain_model.vocabulary import PGTERMS
from gutenberg._util.logging import disable_logging
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove


_METADATA_CACHE = local_path(os.path.join('metadata', 'metadata.db'))
_METADATA_DATABASE_SINGLETON = None


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


def _populate_metadata_graph(graph):
    """Downloads the Project Gutenberg metadata dump and persists it to disk.

    """
    graph.open(_METADATA_CACHE, create=True)
    with contextlib.closing(graph):
        with _download_metadata_archive() as metadata_archive:
            for fact in _iter_metadata_triples(metadata_archive):
                graph.add(fact)


def _create_metadata_graph(store='Sleepycat'):
    """Returns a persistable RDF graph.

    """
    return Graph(store=store, identifier='urn:gutenberg:metadata')


def _reset_metadata_graph():
    """Removes all traces of the persistent RDF graph.

    """
    global _METADATA_DATABASE_SINGLETON
    _METADATA_DATABASE_SINGLETON = None
    remove(_METADATA_CACHE)


def _open_or_create_metadata_graph():
    """Connects to the persistent RDF graph (creating the graph if necessary).

    """
    global _METADATA_DATABASE_SINGLETON
    _METADATA_DATABASE_SINGLETON = _create_metadata_graph()
    if not os.path.exists(_METADATA_CACHE):
        makedirs(_METADATA_CACHE)
        _populate_metadata_graph(_METADATA_DATABASE_SINGLETON)
    _METADATA_DATABASE_SINGLETON.open(_METADATA_CACHE, create=False)
    return _add_namespaces(_METADATA_DATABASE_SINGLETON)


def load_metadata(refresh_cache=False):
    """Returns a graph representing meta-data for all Project Gutenberg texts.
    Pertinent information about texts or about how texts relate to each other
    (e.g. shared authors, shared subjects) can be extracted using standard RDF
    processing techniques (e.g. SPARQL queries). After making an initial remote
    call to Project Gutenberg's servers, the meta-data is persisted locally.

    """
    if refresh_cache:
        _reset_metadata_graph()

    if _METADATA_DATABASE_SINGLETON is not None:
        return _METADATA_DATABASE_SINGLETON

    return _open_or_create_metadata_graph()
