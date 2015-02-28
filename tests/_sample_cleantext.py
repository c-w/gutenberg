# pylint: disable=C0111
# pylint: disable=R0903


from __future__ import absolute_import
import os
import sys

from gutenberg._util.os import determine_encoding


class SampleCleanText(object):
    def __init__(self, etextno, text):
        self.etextno = etextno
        self.text = text

    @classmethod
    def for_etextno(cls, etextno):
        return SampleCleanText(etextno, _load_cleantext(etextno))

    @staticmethod
    def all():
        for etextno in os.listdir(_cleantext_data_path()):
            yield SampleCleanText.for_etextno(int(etextno))


def _cleantext_data_path():
    module = os.path.dirname(sys.modules['tests'].__file__)
    return os.path.join(module, 'data', 'clean-texts')


def _load_cleantext(etextno):
    data_path = os.path.join(_cleantext_data_path(), str(etextno))
    encoding = determine_encoding(data_path, 'utf-8')
    return open(data_path).read().decode(encoding)
