# -*- coding: utf-8 -*-
# pylint: disable=C0111
# pylint: disable=W0142


from __future__ import absolute_import
import itertools
import json
import os
import sys


class SampleMetaData(object):
    __uids = {}

    def __init__(self, etextno, authors=frozenset(), titles=frozenset()):
        self.author = frozenset(authors)
        self.title = frozenset(titles)
        self.etextno = etextno or self.__create_uid(self.author | self.title)

    @classmethod
    def __create_uid(cls, hashable):
        return cls.__uids.setdefault(hashable, len(cls.__uids) + 1)

    def _rdf_etextno(self):
        return (
            u'<http://www.gutenberg.org/ebooks/{etextno}> '
            u'<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> '
            u'<http://www.gutenberg.org/2009/pgterms/ebook> '
            u'.'
        ).format(etextno=self.etextno)

    def _rdf_author(self):
        return u'' if not self.author else u'\n'.join(
            u'<http://www.gutenberg.org/ebooks/{etextno}> '
            u'<http://purl.org/dc/terms/creator> '
            u'<http://www.gutenberg.org/2009/agents/{agent}> '
            u'.\n'
            u'<http://www.gutenberg.org/2009/agents/{agent}> '
            u'<http://www.gutenberg.org/2009/pgterms/alias> '
            u'"{author}" '
            u'.'
            .format(etextno=self.etextno, author=author,
                    agent=self.__create_uid(author))
            for author in self.author)

    def _rdf_title(self):
        return u'' if not self.title else u'\n'.join(
            u'<http://www.gutenberg.org/ebooks/{etextno}> '
            u'<http://purl.org/dc/terms/title> '
            u'"{title}"'
            u'.'
            .format(etextno=self.etextno, title=title)
            for title in self.title)

    def rdf(self):
        return '\n'.join(itertools.ifilter(None, [
            self._rdf_etextno(),
            self._rdf_author(),
            self._rdf_title(),
        ]))

    @classmethod
    def for_etextno(cls, etextno):
        metadata = _load_metadata(etextno)
        return SampleMetaData(etextno, **metadata)

    @staticmethod
    def all():
        for etextno in os.listdir(_sample_metadata_path()):
            yield SampleMetaData.for_etextno(int(etextno))


def _sample_metadata_path():
    module = os.path.dirname(sys.modules['tests'].__file__)
    return os.path.join(module, 'data', 'sample-metadata')


def _load_metadata(etextno):
    data_path = os.path.join(_sample_metadata_path(), str(etextno))
    return json.load(open(data_path))
