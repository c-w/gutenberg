# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
import unittest
import tempfile
import os
import sys
import urllib

import gutenberg.acquire.metadata
from gutenberg.query import get_metadata
from gutenberg.acquire.metadata import InvalidCacheException

from rdflib.plugin import PluginException

from six import u

class TestSleepycat(unittest.TestCase):
    def _get_manager(self):
        cache_uri = tempfile.mktemp()
        mgr = gutenberg.acquire.metadata.MetadataCacheManager(
                store='Sleepycat', cache_uri=cache_uri)
        mgr.catalog_source = "file://%s" % (
                urllib.pathname2url(_sample_metadata_rdf_file_path()))
        return mgr

    def test_read_unpopulated_cache(self):
        mgr = self._get_manager()
        gutenberg.acquire.metadata.set_metadata_cache_manager(mgr)
        try:
            title = get_metadata('title', 50405)
        except InvalidCacheException:
            pass
        except:
            raise
        finally:
            gutenberg.acquire.metadata.set_metadata_cache_manager(None)

    def test_populate(self):
        mgr = self._get_manager()
        mgr.populate()
        gutenberg.acquire.metadata.set_metadata_cache_manager(mgr)
        title = get_metadata('title', 50405)
        assert(title != '')
        gutenberg.acquire.metadata.set_metadata_cache_manager(None)
        mgr.close()
        mgr.delete()


class TestSqlite(unittest.TestCase):
    def _get_manager(self):
        sqlite_filename = "%s.sqlite" % tempfile.mktemp()
        cache_uri = "sqlite:///%s" % sqlite_filename
        try:
            mgr = gutenberg.acquire.metadata.MetadataCacheManager(
                    store='SQLAlchemy', cache_uri=cache_uri)
        except PluginException as exception:
            self.skipTest("SQLAlchemy plugin not installed: %s" %
                    str(exception))
        mgr.catalog_source = "file://%s" % (
                urllib.pathname2url(_sample_metadata_rdf_file_path()))
        return mgr

    def test_populate(self):
        mgr = self._get_manager()
        mgr.populate()
                
        gutenberg.acquire.metadata.set_metadata_cache_manager(mgr)
        title = get_metadata('title', 50405)
        assert(title != '')
        gutenberg.acquire.metadata.set_metadata_cache_manager(None)
        mgr.close()
        mgr.delete()


def _sample_metadata_rdf_file_path():
    module = os.path.dirname(sys.modules['tests'].__file__)
    return os.path.join(module, 'data', 'sample-rdf-files.tar.bz2')

if __name__ == '__main__':
    unittest.main()
