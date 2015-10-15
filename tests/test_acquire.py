# -*- coding: utf-8 -*-
# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
from builtins import str
import itertools
import unittest

from gutenberg._domain_model.vocabulary import DCTERMS
from gutenberg._domain_model.vocabulary import PGTERMS
from tests._sample_metadata import SampleMetaData
from tests._util import MockMetadataMixin
from tests._util import MockTextMixin

from gutenberg.acquire import load_etext
from gutenberg.acquire import load_metadata


class TestLoadMetadata(MockMetadataMixin, unittest.TestCase):
    def sample_data(self):
        return SampleMetaData.all()

    def test_load_metadata(self):
        metadata = load_metadata()
        self.assertTrue(len(list(metadata[::PGTERMS.ebook])) > 0)
        self.assertTrue(len(list(metadata[:DCTERMS.creator:])) > 0)
        self.assertTrue(len(list(metadata[:DCTERMS.title:])) > 0)


class TestLoadEtext(MockTextMixin, unittest.TestCase):
    def test_load_etext(self):
        loaders = (lambda etextno: load_etext(etextno, refresh_cache=True),
                   lambda etextno: load_etext(etextno, refresh_cache=False))
        testcases = (
            SampleMetaData.for_etextno(2701),   # newstyle identifier
            SampleMetaData.for_etextno(5),      # oldstyle identifier
            SampleMetaData.for_etextno(14287),  # unicode text
            SampleMetaData.for_etextno(23962)   # UTF-8 text
        )
        for testcase, loader in itertools.product(testcases, loaders):
            text = loader(testcase.etextno)
            self.assertTrue(isinstance(text, str))


if __name__ == '__main__':
    unittest.main()
