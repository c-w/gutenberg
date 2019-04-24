# -*- coding: utf-8 -*-
# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import, unicode_literals
from builtins import str
import itertools
import unittest
import re

import responses

from gutenberg._domain_model.exceptions import UnknownDownloadUriException
from gutenberg._domain_model.vocabulary import DCTERMS
from gutenberg._domain_model.vocabulary import PGTERMS
from tests._sample_metadata import SampleMetaData
from tests._util import INTEGRATION_TESTS_ENABLED
from tests._util import MockMetadataMixin
from tests._util import MockTextMixin

from gutenberg.acquire import text
from gutenberg.acquire import load_etext
from gutenberg.acquire import load_metadata


class TestLoadMetadata(MockMetadataMixin, unittest.TestCase):
    def sample_data(self):
        return SampleMetaData.all()

    def test_load_metadata(self):
        metadata = load_metadata()
        self.assertGreater(len(list(metadata[::PGTERMS.ebook])), 0)
        self.assertGreater(len(list(metadata[:DCTERMS.creator:])), 0)
        self.assertGreater(len(list(metadata[:DCTERMS.title:])), 0)


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
            etext = loader(testcase.etextno)
            self.assertIsInstance(etext, str)
            self.assertNotIn('\ufffd', etext)

    @responses.activate
    def test_invalid_etext(self):
        with self.assertRaises(UnknownDownloadUriException):
            text.load_etext(1, mirror='http://example.com')


@unittest.skipUnless(INTEGRATION_TESTS_ENABLED, reason='unit-tests only')
class TestLoadEtextNetworked(unittest.TestCase):
    def test_load_etext(self):
        etext = text.load_etext(2701)
        self.assertIsInstance(etext, str)
        self.assertGreater(len(etext), 1000)


class TestFailLoadEtext(unittest.TestCase):
    def request_head_response(self, ok=False):
        status = 200 if ok else 404
        responses.add(responses.HEAD, text._GUTENBERG_MIRROR, status=status)

    @responses.activate
    def test_unreachable_mirror(self):
        self.request_head_response(ok=False)

        with self.assertRaises(UnknownDownloadUriException):
            text.load_etext(1)


class TestExtensionsLoadEtext(unittest.TestCase):
    def request_head_response(self, valid_files):
        responses.add(responses.HEAD, text._GUTENBERG_MIRROR, status=200)

        for valid_file in valid_files:
            url = re.compile('^.*{}$'.format(valid_file))
            responses.add(responses.HEAD, url, status=200)

    @responses.activate
    def test_extensions_order_utf8_only(self):
        utf8_filename = '12345-0.txt'
        self.request_head_response(valid_files=[utf8_filename])

        extensions = text._format_download_uri(12345)
        self.assertEqual(extensions.split('/')[-1], utf8_filename)

        extensions = text._format_download_uri(12345, prefer_ascii=False)
        self.assertEqual(extensions.split('/')[-1], utf8_filename)

    @responses.activate
    def test_extensions_order_ascii_only(self):
        ascii_filename = '12345.txt'
        self.request_head_response(valid_files=[ascii_filename])

        extensions = text._format_download_uri(12345)
        self.assertEqual(extensions.split('/')[-1], ascii_filename)

        extensions = text._format_download_uri(12345, prefer_ascii=True)
        self.assertEqual(extensions.split('/')[-1], ascii_filename)

    @responses.activate
    def test_extensions_order_utf8_first(self):
        utf8_filename = '12345-0.txt'
        all_files = ['12345.txt', '12345-8.txt', '12345-0.txt']
        self.request_head_response(valid_files=all_files)

        extensions = text._format_download_uri(12345)
        self.assertEqual(extensions.split('/')[-1], utf8_filename)

        extensions = text._format_download_uri(12345, prefer_ascii=False)
        self.assertEqual(extensions.split('/')[-1], utf8_filename)

    @responses.activate
    def test_extensions_order_ascii_first(self):
        ascii_filename = '12345.txt'
        all_files = ['12345-8.txt', '12345-0.txt', '12345.txt']
        self.request_head_response(valid_files=all_files)

        extensions = text._format_download_uri(12345)
        self.assertNotEqual(extensions.split('/')[-1], ascii_filename)

        extensions = text._format_download_uri(12345, prefer_ascii=True)
        self.assertEqual(extensions.split('/')[-1], ascii_filename)

    @responses.activate
    def test_extensions_order_eightbit_first(self):
        eightbit_filename = '12345-8.txt'
        ascii_filename = '12345.txt'
        all_files = ['12345-8.txt', '12345.txt']
        self.request_head_response(valid_files=all_files)

        extensions = text._format_download_uri(12345)
        self.assertEqual(extensions.split('/')[-1], eightbit_filename)

        extensions = text._format_download_uri(12345, prefer_ascii=True)
        self.assertEqual(extensions.split('/')[-1], ascii_filename)


if __name__ == '__main__':
    unittest.main()
