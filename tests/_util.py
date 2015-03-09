# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=R0921
# pylint: disable=W0212


from __future__ import absolute_import
import abc
import gzip
import os
import shutil
import tempfile

import gutenberg.acquire.metadata
import gutenberg.acquire.text


class MockTextMixin(object):
    def setUp(self):
        self.mock_text_cache = tempfile.mkdtemp()
        gutenberg.acquire.text._TEXT_CACHE = self.mock_text_cache

    def tearDown(self):
        shutil.rmtree(self.mock_text_cache)


class MockMetadataMixin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def sample_data(self):
        raise NotImplementedError

    def setUp(self):
        self.mock_metadata_cache = _mock_metadata_cache(self.sample_data())
        gutenberg.acquire.metadata._METADATA_CACHE = self.mock_metadata_cache

    def tearDown(self):
        os.remove(self.mock_metadata_cache)


def _mock_metadata_cache(sample_datas):
    with tempfile.NamedTemporaryFile(delete=False) as metadata_file:
        with gzip.GzipFile(fileobj=metadata_file, mode='wb') as gzip_file:
            contents = u'\n'.join(item.rdf() for item in sample_datas)
            gzip_file.write(contents.encode('utf-8'))
    return metadata_file.name
