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

from rdflib import plugin, Literal, URIRef
from rdflib.graph import Graph
from rdflib.term import URIRef
from rdflib.store import Store

from gutenberg._domain_model.persistence import local_path
from gutenberg._domain_model.vocabulary import DCTERMS
from gutenberg._domain_model.vocabulary import PGTERMS
from gutenberg._util.logging import disable_logging
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove


_GUTENBERG_CATALOG_URL = \
    r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'


class CacheAlreadyExistsException(Exception):
    pass

class CacheDeleteException(Exception):
    pass

class InvalidCacheException(Exception):
    pass

class MetadataCacheManager(object):
    def __init__(self, store, cache_uri):
        self.identifier='urn:gutenberg:metadata'
        if store == 'Sleepycat':
            self.store = store
            self.removable = True
        else:
            if cache_uri.startswith('sqlite://'):
                self.removable = True
            else:
                self.removable = False
            self.store = plugin.get(store, Store)(identifier=self.identifier)
        self.cache_uri = cache_uri

        self.graph = Graph(store=self.store, identifier=self.identifier)
        self.cache_open = False

        self.catalog_source = _GUTENBERG_CATALOG_URL

    def exists(self):
        """Detect if the cache exists.

        """
        # If the cache is removable it has some local structure we can check
        # to see if it exists.
        if self.removable:
            return os.path.exists(self._get_local_storage_path())

        # If there is no local structure, the best we can do is see if the
        # storage contains a valid graph.
        test_graph = Graph(store=self.store, identifier=self.identifier)
        try:
            test_graph.open(self.cache_uri, create=False)
            self._add_namespaces(test_graph)
            test_graph.close()
            return True
        except:
            return False

    def open(self):
        """Opens an existing cache.

        """
        try:
            self.graph.open(self.cache_uri, create=False)
            self._add_namespaces(self.graph)
            self.cache_open = True
        except:
            raise InvalidCacheException("The cache is invalid or not created")

    def close(self):
        """Closes an opened cache.

        """
        self.graph.close()
        self.cache_open = False

    def delete(self):
        """Delete the cache.

        """
        self.close()
        if self.removable:
            remove(self._get_local_storage_path())
        else:
            raise CacheDeleteException("Graph store type is not removable")

    def populate(self, data_override=None):
        """Populates a new cache.

        """
        if self.exists():
            raise CacheAlreadyExistsException(
                    "location: %s" % self.cache_uri)

        if self.store == 'Sleepycat':
            makedirs(self.cache_uri)

        self.graph.open(self.cache_uri, create=True)

        if data_override:
            # Allow callers to override the data being populated, almost
            # exclusively for automated testing
            (data, format) = data_override
            with contextlib.closing(self.graph):
                self.graph.parse(data=data, format=format)
            return

        with contextlib.closing(self.graph):
            with self._download_metadata_archive() as metadata_archive:
                for fact in _iter_metadata_triples(metadata_archive):
                    self.graph.add(fact)

    def refresh(self):
        """Refresh the cache by deleting the old one and creating a new one.

        """
        if self.exists():
            self.delete()
        self.populate()
        self.open()

    def _get_local_storage_path(self):
        if self.cache_uri.startswith('sqlite://'):
            filepath = self.cache_uri[9:]
        else:
            filepath = self.cache_uri
        return filepath

    def _add_namespaces(self, graph):
        """Function to ensure that the graph always has some specific namespace
        aliases set.

        """
        graph.bind('pgterms', PGTERMS)
        graph.bind('dcterms', DCTERMS)

    @contextlib.contextmanager
    def _download_metadata_archive(self):
        """Makes a remote call to the Project Gutenberg servers and downloads the
        entire Project Gutenberg meta-data catalog. The catalog describes the texts
        on Project Gutenberg in RDF. The function returns a file-pointer to the
        catalog.

        """
        with tempfile.NamedTemporaryFile(delete=False) as metadata_archive:
            shutil.copyfileobj(urllib2.urlopen(self.catalog_source), metadata_archive)
        yield metadata_archive.name
        remove(metadata_archive.name)


def _iter_metadata_triples(metadata_archive_path):
    """Yields all meta-data of Project Gutenberg texts contained in the catalog
    dump.

    """
    is_invalid = lambda token: isinstance(token, URIRef) and ' ' in token
    with contextlib.closing(tarfile.open(metadata_archive_path)) \
            as metadata_archive:
        for item in metadata_archive:
            if re.match(r'^.*pg(?P<etextno>\d+).rdf$', item.name):
                with disable_logging():
                    graph = Graph().parse(metadata_archive.extractfile(item))
                for fact in graph:
                    if not any(is_invalid(token) for token in fact):
                        yield fact
                    else:
                        logging.info('skipping invalid triple %s', fact)


_METADATA_CACHE_MANAGER = MetadataCacheManager(store='Sleepycat',
    cache_uri=local_path(os.path.join('metadata', 'metadata.db')))


def set_metadata_cache_manager(cache_manager):
    """Sets the metadata cache object to use.

    """
    global _METADATA_CACHE_MANAGER
    if _METADATA_CACHE_MANAGER and _METADATA_CACHE_MANAGER.cache_open:
        _METADATA_CACHE_MANAGER.close()

    _METADATA_CACHE_MANAGER = cache_manager


def get_metadata_cache_manager():
    """Returns the current metadata cache manager object.

    """
    global _METADATA_CACHE_MANAGER
    return _METADATA_CACHE_MANAGER


def load_metadata(refresh_cache=False):
    """Returns a graph representing meta-data for all Project Gutenberg texts.
    Pertinent information about texts or about how texts relate to each other
    (e.g. shared authors, shared subjects) can be extracted using standard RDF
    processing techniques (e.g. SPARQL queries). After making an initial remote
    call to Project Gutenberg's servers, the meta-data is persisted locally.

    """
    global _METADATA_CACHE_MANAGER

    if refresh_cache:
        _METADATA_CACHE_MANAGER.refresh()

    if _METADATA_CACHE_MANAGER.cache_open:
        return _METADATA_CACHE_MANAGER.graph

    _METADATA_CACHE_MANAGER.open()

    return _METADATA_CACHE_MANAGER.graph
