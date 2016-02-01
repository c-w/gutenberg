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

from gutenberg.acquire.metadata import MetadataCacheManager
from gutenberg.acquire.metadata import set_metadata_cache_manager
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
        self.mgr = _TestMetadataCacheManager(self.sample_data, data_format='nt')
        self.mgr.populate()
        set_metadata_cache_manager(self.mgr)

    def tearDown(self):
        set_metadata_cache_manager(None)
        self.mgr.delete()


class _TestMetadataCacheManager(MetadataCacheManager):
    def __init__(self, sample_data_factory, data_format):
        MetadataCacheManager.__init__(self, 'Sleepycat', tempfile.mktemp())
        self.sample_data_factory = sample_data_factory
        self.data_format = data_format

    def populate(self):
        MetadataCacheManager.populate(self)

        data = u('\n').join(item.rdf() for item in self.sample_data_factory())

        self.graph.open(self.cache_uri, create=True)
        with contextlib.closing(self.graph):
            self.graph.parse(data=data, format=self.data_format)

    @contextlib.contextmanager
    def _download_metadata_archive(self):
        yield None

    @classmethod
    def _iter_metadata_triples(cls, metadata_archive_path):
        return []
