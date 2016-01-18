# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
import unittest
import tempfile
import os
import sys
try:
    from urllib import pathname2url
except ImportError:
    from urllib.request import pathname2url

import gutenberg.acquire.metadata
from gutenberg.query import get_metadata
from gutenberg.acquire.metadata import InvalidCacheException, CacheAlreadyExistsException

from rdflib.plugin import PluginException

from six import u

class MetadataCacheManager(object):
    def test_read_unpopulated_cache(self):
        gutenberg.acquire.metadata.set_metadata_cache_manager(self.manager)
        try:
            title = get_metadata('title', 50405)
        except InvalidCacheException:
            pass
        except:
            raise

    def test_initialize(self):
        # Simply creating the cache manager shouldn't create on-disk structures
        if not self.local_storage:
            self.skipTest("Storage type does not have on-disk structures")

        assert(os.path.exists(self.local_storage) == False)

    def test_populate(self):
        self.manager.populate()
        gutenberg.acquire.metadata.set_metadata_cache_manager(self.manager)
        title = get_metadata('title', 50405)
        assert(title != '')

    def test_repopulate(self):
        self.manager.populate()
        gutenberg.acquire.metadata.set_metadata_cache_manager(self.manager)
        self.manager.delete()
        self.manager.populate()
        title = get_metadata('title', 50405)
        assert(title != '')

    def test_refresh(self):
        self.manager.populate()
        self.manager.refresh()

    def test_repopulate_without_delete(self):
        # Trying to populate an existing cache should raise an exception
        self.manager.populate()
        try:
            self.manager.populate()
        except CacheAlreadyExistsException:
            pass
        except:
            raise

    def test_delete(self):
        if not self.manager.removable:
            self.skipTest("Storage type is not removable")

        assert(os.path.exists(self.local_storage) == False)
        self.manager.populate()
        assert(os.path.exists(self.local_storage) == True)
        self.manager.delete()
        assert(os.path.exists(self.local_storage) == False)

    def test_read_deleted_cache(self):
        self.manager.populate()
        gutenberg.acquire.metadata.set_metadata_cache_manager(self.manager)
        self.manager.delete()
        try:
            title = get_metadata('title', 50405)
        except InvalidCacheException:
            pass
        except:
            raise

    def tearDown(self):
        gutenberg.acquire.metadata.set_metadata_cache_manager(None)
        if self.manager.cache_open:
            self.manager.delete()
        self.manager = None


class TestSleepycat(MetadataCacheManager, unittest.TestCase):
    def setUp(self):
        self.local_storage = tempfile.mktemp()
        self.manager = gutenberg.acquire.metadata.MetadataCacheManager(
                store='Sleepycat', cache_uri=self.local_storage)
        self.manager.catalog_source = "file://%s" % (
                pathname2url(_sample_metadata_rdf_file_path()))


class TestSqlite(MetadataCacheManager, unittest.TestCase):
    def setUp(self):
        self.local_storage = "%s.sqlite" % tempfile.mktemp()
        cache_uri = "sqlite:///%s" % self.local_storage
        try:
            self.manager = gutenberg.acquire.metadata.MetadataCacheManager(
                    store='SQLAlchemy', cache_uri=cache_uri)
        except PluginException as exception:
            self.skipTest("SQLAlchemy plugin not installed: %s" %
                    str(exception))
        self.manager.catalog_source = "file://%s" % (
                pathname2url(_sample_metadata_rdf_file_path()))

def _sample_metadata_rdf_file_path():
    module = os.path.dirname(sys.modules['tests'].__file__)
    return os.path.join(module, 'data', 'sample-rdf-files.tar.bz2')

if __name__ == '__main__':
    unittest.main()
