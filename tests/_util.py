# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0921
# pylint: disable=W0212


from __future__ import absolute_import
import abc
import contextlib
import shutil
import tempfile

from six import u
from six import with_metaclass

import gutenberg.acquire.metadata
import gutenberg.acquire.text


# noinspection PyPep8Naming,PyAttributeOutsideInit
class MockTextMixin(object):
    def setUp(self):
        self.mock_text_cache = tempfile.mkdtemp()
        gutenberg.acquire.text._TEXT_CACHE = self.mock_text_cache

    def tearDown(self):
        shutil.rmtree(self.mock_text_cache)


# noinspection PyPep8Naming,PyAttributeOutsideInit
class MockMetadataMixin(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def sample_data(self):
        raise NotImplementedError

    def setUp(self):
        metadata_directory = tempfile.mktemp()
        self.mgr = gutenberg.acquire.metadata.MetadataCacheManager(
                store='Sleepycat', cache_uri=metadata_directory)
        data = u('\n').join(item.rdf() for item in self.sample_data())
        self.mgr.populate(data_override=(data, 'nt'))
        gutenberg.acquire.metadata.set_metadata_cache_manager(self.mgr)

    def tearDown(self):
        gutenberg.acquire.metadata.set_metadata_cache_manager(None)
        self.mgr.delete()
