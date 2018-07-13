"""Module to deal with metadata acquisition."""
# pylint:disable=W0603

from __future__ import absolute_import, unicode_literals

import abc
import codecs
import logging
import os
import re
import shutil
import tarfile
import tempfile
from contextlib import closing
from contextlib import contextmanager

from rdflib import plugin
from rdflib.graph import Graph
from rdflib.query import ResultException
from rdflib.store import Store
from rdflib.term import BNode
from rdflib.term import URIRef
from rdflib_sqlalchemy import registerplugins
from six import text_type
from six import with_metaclass

from gutenberg._domain_model.exceptions import CacheAlreadyExistsException
from gutenberg._domain_model.exceptions import InvalidCacheException
from gutenberg._domain_model.persistence import local_path
from gutenberg._domain_model.vocabulary import DCTERMS
from gutenberg._domain_model.vocabulary import PGTERMS
from gutenberg._util.logging import disable_logging
from gutenberg._util.os import makedirs
from gutenberg._util.os import remove
from gutenberg._util.url import urlopen

_GUTENBERG_CATALOG_URL = \
    r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'
_DB_IDENTIFIER = 'urn:gutenberg:metadata'
_DB_PATH = local_path(os.path.join('metadata', 'metadata.db'))


class MetadataCache(with_metaclass(abc.ABCMeta, object)):
    """Super-class for all metadata cache implementations.

    """
    def __init__(self, store, cache_uri):
        self.store = store
        self.cache_uri = cache_uri
        self.graph = Graph(store=self.store, identifier=_DB_IDENTIFIER)
        self.is_open = False
        self.catalog_source = _GUTENBERG_CATALOG_URL

    @property
    def exists(self):
        """Detect if the cache exists.

        """
        return os.path.exists(self._local_storage_path)

    def open(self):
        """Opens an existing cache.

        """
        try:
            self.graph.open(self.cache_uri, create=False)
            self._add_namespaces(self.graph)
            self.is_open = True
        except Exception:
            raise InvalidCacheException('The cache is invalid or not created')

    def close(self):
        """Closes an opened cache.

        """
        self.graph.close()
        self.is_open = False

    def delete(self):
        """Delete the cache.

        """
        self.close()
        remove(self._local_storage_path)

    def populate(self):
        """Populates a new cache.

        """
        if self.exists:
            raise CacheAlreadyExistsException('location: %s' % self.cache_uri)

        self._populate_setup()

        with closing(self.graph):
            with self._download_metadata_archive() as metadata_archive:
                for fact in self._iter_metadata_triples(metadata_archive):
                    self._add_to_graph(fact)

    def _add_to_graph(self, fact):
        """Adds a (subject, predicate, object) RDF triple to the graph.

        """
        self.graph.add(fact)

    def _populate_setup(self):
        """Executes operations necessary before the cache can be populated.

        """
        pass

    def refresh(self):
        """Refresh the cache by deleting the old one and creating a new one.

        """
        if self.exists:
            self.delete()
        self.populate()
        self.open()

    @property
    def _local_storage_path(self):
        """Returns a path to the on-disk structure of the cache.

        """
        return self.cache_uri

    @staticmethod
    def _add_namespaces(graph):
        """Function to ensure that the graph always has some specific namespace
        aliases set.

        """
        graph.bind('pgterms', PGTERMS)
        graph.bind('dcterms', DCTERMS)

    @contextmanager
    def _download_metadata_archive(self):
        """Makes a remote call to the Project Gutenberg servers and downloads
        the entire Project Gutenberg meta-data catalog. The catalog describes
        the texts on Project Gutenberg in RDF. The function returns a
        file-pointer to the catalog.

        """
        with tempfile.NamedTemporaryFile(delete=False) as metadata_archive:
            shutil.copyfileobj(urlopen(self.catalog_source), metadata_archive)
        yield metadata_archive.name
        remove(metadata_archive.name)

    @classmethod
    def _metadata_is_invalid(cls, fact):
        """Determines if the fact is not well formed.

        """
        return any(isinstance(token, URIRef) and ' ' in token
                   for token in fact)

    @classmethod
    def _iter_metadata_triples(cls, metadata_archive_path):
        """Yields all meta-data of Project Gutenberg texts contained in the
        catalog dump.

        """
        pg_rdf_regex = re.compile(r'pg\d+.rdf$')
        with closing(tarfile.open(metadata_archive_path)) as metadata_archive:
            for item in metadata_archive:
                if pg_rdf_regex.search(item.name):
                    with disable_logging():
                        extracted = metadata_archive.extractfile(item)
                        graph = Graph().parse(extracted)
                    for fact in graph:
                        if cls._metadata_is_invalid(fact):
                            logging.info('skipping invalid triple %s', fact)
                        else:
                            yield fact


class SleepycatMetadataCache(MetadataCache):
    """Default cache manager implementation, based on Sleepycat/Berkeley DB.
    Sleepycat is natively supported by RDFlib so this cache is reasonably fast.

    """
    def __init__(self, cache_location):
        self._check_can_be_instantiated()
        cache_uri = cache_location
        store = 'Sleepycat'
        MetadataCache.__init__(self, store, cache_uri)

    def _populate_setup(self):
        makedirs(self.cache_uri)
        self.graph.open(self.cache_uri, create=True)

    @classmethod
    def _check_can_be_instantiated(cls):
        try:
            from bsddb import db
        except ImportError:
            try:
                from bsddb3 import db
            except ImportError:
                db = None
        if db is None:
            raise InvalidCacheException('no install of bsddb/bsddb3 found')
        del db


class FusekiMetadataCache(MetadataCache):
    _CACHE_URL_PREFIXES = ('http://', 'https://')

    def __init__(self, cache_location, cache_url, user=None, password=None):
        self._check_can_be_instantiated(cache_url)
        store = 'SPARQLUpdateStore'
        MetadataCache.__init__(self, store, cache_url)
        user = user or os.getenv('GUTENBERG_FUSEKI_USER')
        password = password or os.getenv('GUTENBERG_FUSEKI_PASSWORD')
        self.graph.store.setCredentials(user, password)
        self._cache_marker = cache_location

    def _populate_setup(self):
        """Just create a local marker file since the actual database should
        already be created on the Fuseki server.

        """
        makedirs(os.path.dirname(self._cache_marker))
        with codecs.open(self._cache_marker, 'w', encoding='utf-8') as fobj:
            fobj.write(self.cache_uri)
        self.graph.open(self.cache_uri)

    def delete(self):
        """Deletes the local marker file and also any data in the Fuseki
        server.

        """
        MetadataCache.delete(self)
        try:
            self.graph.query('DELETE WHERE { ?s ?p ?o . }')
        except ResultException:
            # this is often just a false positive since Jena Fuseki does not
            # return tuples for a deletion query, so swallowing the exception
            # here is fine
            logging.exception('error when deleting graph')

    @property
    def _local_storage_path(self):
        """Returns the path to the local marker file that gets written when
        the cache was created.

        """
        return self._cache_marker

    @classmethod
    def _check_can_be_instantiated(cls, cache_location):
        """Pre-conditions: the cache location is the URL to a Fuseki server
        and the SPARQLWrapper library exists (transitive dependency of
        RDFlib's sparqlstore).

        """
        if not any(cache_location.startswith(prefix)
                   for prefix in cls._CACHE_URL_PREFIXES):
            raise InvalidCacheException('cache location is not a Fuseki url')

        try:
            from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
        except ImportError:
            raise InvalidCacheException('unable to import sparql store')
        del SPARQLUpdateStore

    @classmethod
    def _metadata_is_invalid(cls, fact):
        """Filters out blank nodes since the SPARQLUpdateStore does not
        support them.

        """
        return (MetadataCache._metadata_is_invalid(fact)
                or any(isinstance(token, BNode) for token in fact))


class SqliteMetadataCache(MetadataCache):
    """Cache manager based on SQLite and the RDFlib plugin for SQLAlchemy.
    Quite slow.

    """
    _CACHE_URI_PREFIX = 'sqlite:///'

    def __init__(self, cache_location):
        cache_uri = self._CACHE_URI_PREFIX + cache_location
        store = plugin.get('SQLAlchemy', Store)(identifier=_DB_IDENTIFIER)
        MetadataCache.__init__(self, store, cache_uri)

    def _populate_setup(self):
        self.graph.open(self.cache_uri, create=True)

    @property
    def _local_storage_path(self):
        return self.cache_uri[len(self._CACHE_URI_PREFIX):]

    def _add_to_graph(self, fact):
        try:
            self.graph.add(fact)
        except Exception as ex:
            self.graph.rollback()
            if not self._is_graph_add_exception_acceptable(ex):
                raise ex
        else:
            self.graph.commit()

    @classmethod
    def _is_graph_add_exception_acceptable(cls, ex):
        """Checks if a graph-add exception can be safely ignored.

        """
        # integrity errors due to violating unique constraints should be safe
        # to ignore since the only unique constraints in rdflib-sqlalchemy are
        # on index columns
        return 'UNIQUE constraint failed' in text_type(ex)


_METADATA_CACHE = None

registerplugins()


def set_metadata_cache(cache):
    """Sets the metadata cache object to use.

    """
    global _METADATA_CACHE

    if _METADATA_CACHE and _METADATA_CACHE.is_open:
        _METADATA_CACHE.close()

    _METADATA_CACHE = cache


def get_metadata_cache():
    """Returns the current metadata cache object.

    """
    global _METADATA_CACHE

    if _METADATA_CACHE is None:
        _METADATA_CACHE = _create_metadata_cache(_DB_PATH)

    return _METADATA_CACHE


def _create_metadata_cache(cache_location):
    """Creates a new metadata cache instance appropriate for this platform.

    """
    cache_url = os.getenv('GUTENBERG_FUSEKI_URL')
    if cache_url:
        return FusekiMetadataCache(cache_location, cache_url)

    try:
        return SleepycatMetadataCache(cache_location)
    except InvalidCacheException:
        logging.warning('Unable to create cache based on BSD-DB. '
                        'Falling back to SQLite backend. '
                        'Performance may be degraded significantly.')

    return SqliteMetadataCache(cache_location)


def load_metadata(refresh_cache=False):
    """Returns a graph representing meta-data for all Project Gutenberg texts.
    Pertinent information about texts or about how texts relate to each other
    (e.g. shared authors, shared subjects) can be extracted using standard RDF
    processing techniques (e.g. SPARQL queries). After making an initial remote
    call to Project Gutenberg's servers, the meta-data is persisted locally.

    """
    cache = get_metadata_cache()

    if refresh_cache:
        cache.refresh()

    if not cache.is_open:
        cache.open()

    return cache.graph
