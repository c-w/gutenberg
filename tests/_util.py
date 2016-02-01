# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0921
# pylint: disable=W0212


from __future__ import absolute_import

import abc
import shutil
import tempfile
from contextlib import closing
from contextlib import contextmanager

from six import u
from six import with_metaclass

from gutenberg.acquire.metadata import SleepycatMetadataCache
import gutenberg.acquire.metadata
import gutenberg.acquire.text


# noinspection PyPep8Naming,PyAttributeOutsideInit
class MockTextMixin(object):
    def setUp(self):
        self.mock_text_cache = tempfile.mkdtemp()
        set_text_cache(self.mock_text_cache)

    def tearDown(self):
        shutil.rmtree(self.mock_text_cache)


# noinspection PyPep8Naming,PyAttributeOutsideInit
class MockMetadataMixin(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def sample_data(self):
        raise NotImplementedError

    def setUp(self):
        self.cache = _SleepycatMetadataCacheForTesting(self.sample_data, 'nt')
        self.cache.populate()
        set_metadata_cache(self.cache)

    def tearDown(self):
        set_metadata_cache(None)
        self.cache.delete()


class _SleepycatMetadataCacheForTesting(SleepycatMetadataCache):
    def __init__(self, sample_data_factory, data_format):
        SleepycatMetadataCache.__init__(self, tempfile.mktemp())
        self.sample_data_factory = sample_data_factory
        self.data_format = data_format

    def populate(self):
        SleepycatMetadataCache.populate(self)

        data = u('\n').join(item.rdf() for item in self.sample_data_factory())

        self.graph.open(self.cache_uri, create=True)
        with closing(self.graph):
            self.graph.parse(data=data, format=self.data_format)

    @contextmanager
    def _download_metadata_archive(self):
        yield None

    @classmethod
    def _iter_metadata_triples(cls, metadata_archive_path):
        return []


def set_text_cache(cache):
    gutenberg.acquire.text._TEXT_CACHE = cache


def set_metadata_cache(cache):
    old_cache = gutenberg.acquire.metadata._METADATA_CACHE
    if old_cache and old_cache.is_open:
        old_cache.close()

    gutenberg.acquire.metadata._METADATA_CACHE = cache
