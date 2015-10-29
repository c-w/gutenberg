# pylint: disable=C0111
# pylint: disable=R0904


from __future__ import absolute_import
import unittest

from six import u

from tests._sample_metadata import SampleMetaData
from tests._util import MockMetadataMixin

from gutenberg.query import get_etexts
from gutenberg.query import get_metadata


class TestGetMetadata(MockMetadataMixin, unittest.TestCase):
    def sample_data(self):
        return SampleMetaData.all()

    def _run_get_metadata_for_feature(self, feature):
        for testcase in self.sample_data():
            expected = getattr(testcase, feature)
            actual = get_metadata(feature, testcase.etextno)
            self.assertTrue(
                set(actual) == set(expected),
                u('non-matching {feature} for book {etextno}: '
                  'expected={expected} actual={actual}')
                .format(
                    feature=feature,
                    etextno=testcase.etextno,
                    actual=actual,
                    expected=expected))

    def test_get_metadata_title(self):
        self._run_get_metadata_for_feature('title')

    def test_get_metadata_author(self):
        self._run_get_metadata_for_feature('author')


class TestGetEtexts(MockMetadataMixin, unittest.TestCase):
    def sample_data(self):
        return SampleMetaData.all()

    def _run_get_etexts_for_feature(self, feature):
        for testcase in self.sample_data():
            for feature_value in getattr(testcase, feature):
                actual = get_etexts(feature, feature_value)
                self.assertTrue(
                    testcase.etextno in actual,
                    u("didn't retrieve {etextno} when querying for books that "
                      'have {feature}="{feature_value}" (got {actual}).')
                    .format(
                        etextno=testcase.etextno,
                        feature=feature,
                        feature_value=feature_value,
                        actual=actual))

    def test_get_etexts_title(self):
        self._run_get_etexts_for_feature('title')

    def test_get_etexts_author(self):
        self._run_get_etexts_for_feature('author')


if __name__ == '__main__':
    unittest.main()
