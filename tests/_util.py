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


class MockTextMixin(object):
    def setUp(self):
        self.mock_text_cache = tempfile.mkdtemp()
        gutenberg.acquire.text._TEXT_CACHE = self.mock_text_cache

    def tearDown(self):
        shutil.rmtree(self.mock_text_cache)


class MockMetadataMixin(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def sample_data(self):
        raise NotImplementedError

    def setUp(self):
        self.mock_metadata_cache = _mock_metadata_cache(self.sample_data())
        gutenberg.acquire.metadata._METADATA_CACHE = self.mock_metadata_cache

    def tearDown(self):
        shutil.rmtree(self.mock_metadata_cache)


def _mock_metadata_cache(sample_datas):
    data = u('\n').join(item.rdf() for item in sample_datas)
    metadata_directory = tempfile.mkdtemp()
    graph = gutenberg.acquire.metadata._create_metadata_graph()
    graph.open(metadata_directory, create=True)
    with contextlib.closing(graph):
        graph.parse(data=data, format='nt')
    return metadata_directory
