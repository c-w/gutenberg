# -*- coding: utf-8 -*-
# pylint: disable=C0111
# pylint: disable=W0142


from __future__ import absolute_import, unicode_literals
import json
import os
import sys


class SampleMetaData(object):
    __uids = {}

    def __init__(self, etextno, authors=None, titles=None, formaturi=None, rights=None, subject=None, language=None):
        self.author = frozenset(authors or [])
        self.title = frozenset(titles or [])
        self.formaturi = frozenset(formaturi or [])
        self.etextno = etextno or self.__create_uid(self.author | self.title)
        self.rights = frozenset(rights or [])
        self.subject = frozenset(subject or [])
        self.language = frozenset(language or [])

    @classmethod
    def __create_uid(cls, hashable):
        return cls.__uids.setdefault(hashable, len(cls.__uids) + 1)

    def _rdf_etextno(self):
        return (
            '<http://www.gutenberg.org/ebooks/{etextno}> '
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> '
            '<http://www.gutenberg.org/2009/pgterms/ebook> '
            '.'
        ).format(etextno=self.etextno)

    def _rdf_author(self):
        return '' if not self.author else '\n'.join(
            '<http://www.gutenberg.org/ebooks/{etextno}> '
            '<http://purl.org/dc/terms/creator> '
            '<http://www.gutenberg.org/2009/agents/{agent}> '
            '.\n'
            '<http://www.gutenberg.org/2009/agents/{agent}> '
            '<http://www.gutenberg.org/2009/pgterms/alias> '
            '"{author}" '
            '.'
            .format(etextno=self.etextno, author=author,
                    agent=self.__create_uid(author))
            for author in self.author)

    def _rdf_title(self):
        return '' if not self.title else '\n'.join(
            '<http://www.gutenberg.org/ebooks/{etextno}> '
            '<http://purl.org/dc/terms/title> '
            '"{title}"'
            '.'
            .format(etextno=self.etextno, title=title)
            for title in self.title)

    def _rdf_rights(self):
        return '' if not self.rights else '\n'.join(
            '<http://www.gutenberg.org/ebooks/{etextno}> '
             '<http://purl.org/dc/terms/rights> '
            '"{rights}"'
             '.'
            .format(etextno=self.etextno, rights=rights)
            for rights in self.rights)

    def _rdf_subject(self):
        return '' if not self.subject else '\n'.join(
            '<http://www.gutenberg.org/ebooks/{etextno}> '
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#Description>'
            '"{subject}"'
            '.'
            .format(etextno=self.etextno, subject=subject)
            for subject in self.subject)

    def _rdf_language(self):
        return '' if not self.language else '\n'.join(
            '<http://www.gutenberg.org/ebooks/{etextno}> '
            '<http://purl.org/dc/terms/language> '
            '<http://www.w3.org/1999/02/22-rdf-syntax-ns#Description>'
            '"{language}"'
            '.'
            .format(etextno=self.etextno, language=language)
            for language in self.language)

    def _rdf_formaturi(self):
        return '' if not self.formaturi else '\n'.join(
            '<http://www.gutenberg.org/ebooks/{etextno}> '
            '<http://purl.org/dc/terms/hasFormat> '
            '<{formaturi}>'
            '.'
            .format(etextno=self.etextno, formaturi=formaturi)
            for formaturi in self.formaturi)

    def rdf(self):
        return '\n'.join(fact for fact in (
            self._rdf_etextno(),
            self._rdf_author(),
            self._rdf_title(),
            self._rdf_formaturi(),
        ) if fact)

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
