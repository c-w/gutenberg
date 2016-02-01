# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
import tempfile
import os
import sys
from gutenberg.acquire.metadata import SleepycatMetadataCache
from gutenberg.acquire.metadata import SqliteMetadataCache
from gutenberg.acquire.metadata import set_metadata_cache
from gutenberg.query import get_metadata
from gutenberg.acquire.metadata import CacheAlreadyExists
from gutenberg.acquire.metadata import InvalidCache
from gutenberg._util.url import pathname2url
from rdflib.plugin import PluginException
from six import u
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


# noinspection PyPep8Naming,PyAttributeOutsideInit
class MetadataCache(object):
    def test_read_unpopulated_cache(self):
        set_metadata_cache(self.cache)
        try:
            get_metadata('title', 50405)
        except InvalidCache:
            pass
        except:
            raise

    def test_initialize(self):
        # Simply creating the cache shouldn't create on-disk structures
        self.assertFalse(os.path.exists(self.local_storage))

    def test_populate(self):
        self.cache.populate()
        set_metadata_cache(self.cache)
        title = get_metadata('title', 30929)
        self.assertTrue(u('Het loterijbriefje') in title)

    def test_repopulate(self):
        self.cache.populate()
        set_metadata_cache(self.cache)
        self.cache.delete()
        self.cache.populate()
        title = get_metadata('title', 30929)
        self.assertTrue(u('Het loterijbriefje') in title)

    def test_refresh(self):
        self.cache.populate()
        set_metadata_cache(self.cache)
        title = get_metadata('title', 30929)
        self.assertTrue(u('Het loterijbriefje') in title)

        self.cache.refresh()
        title = get_metadata('title', 30929)
        self.assertTrue(u('Het loterijbriefje') in title)

    def test_repopulate_without_delete(self):
        # Trying to populate an existing cache should raise an exception
        self.cache.populate()
        try:
            self.cache.populate()
        except CacheAlreadyExists:
            pass
        except:
            raise

    def test_delete(self):
        self.assertFalse(os.path.exists(self.local_storage))
        self.cache.populate()
        self.assertTrue(os.path.exists(self.local_storage))
        self.cache.delete()
        self.assertFalse(os.path.exists(self.local_storage))

    def test_read_deleted_cache(self):
        self.cache.populate()
        set_metadata_cache(self.cache)
        self.cache.delete()
        try:
            get_metadata('title', 50405)
        except InvalidCache:
            pass
        except:
            raise

    def tearDown(self):
        set_metadata_cache(None)
        if self.cache.is_open:
            self.cache.delete()
        self.cache = None


class TestSleepycat(MetadataCache, unittest.TestCase):
    def setUp(self):
        self.local_storage = tempfile.mktemp()
        self.cache = SleepycatMetadataCache(self.local_storage)
        self.cache.catalog_source = "file://%s" % (
                pathname2url(_sample_metadata_rdf_file_path()))


class TestSqlite(MetadataCache, unittest.TestCase):
    def setUp(self):
        self.local_storage = "%s.sqlite" % tempfile.mktemp()
        cache_uri = "sqlite:///%s" % self.local_storage
        try:
            self.cache = SqliteMetadataCache(cache_uri)
        except PluginException as exception:
            self.skipTest("SQLAlchemy plugin not installed: %s" % exception)
        self.cache.catalog_source = "file://%s" % (
                pathname2url(_sample_metadata_rdf_file_path()))


def _sample_metadata_rdf_file_path():
    module = os.path.dirname(sys.modules['tests'].__file__)
    return os.path.join(module, 'data', 'sample-rdf-files.tar.bz2')


if __name__ == '__main__':
    unittest.main()
