"""Module to tag Project Gutenberg etexts with meta-data."""


from __future__ import absolute_import
import gutenberg.common.functutil as functutil
import collections
import json
import logging
import os
import re
import tarfile
import urllib
import xml.etree.cElementTree as ElementTree


def etextno(lines):
    """Retrieves the id for an etext.

    Args:
        lines (iter): the lines of the etext to search

    Returns:
        int: the id of the etext or None if no such id was found

    """
    etext_re = re.compile(r'e(text|book) #(?P<etextno>\d+)', re.I)
    for line in lines:
        match = etext_re.search(line)
        if match is not None:
            return int(match.group('etextno'))
    return None


@functutil.memoize
def metainfo():
    """Retrieves a database of meta-data about Project Gutenberg etexts.  The
    meta-data always contains at least information about the title and author
    of a work. Optional information includes translator, editor, language, etc.

    Returns:
        dict: a mapping from etext-identifier to etext meta-data

    """
    metadata = collections.defaultdict(dict)
    for xml in raw_metainfo():
        etext = parse_etextno(xml)
        author = parse_author(xml)
        title = parse_title(xml)
        if author is None:
            logging.warning('no author found for etext %s', etext)
        if title is None:
            logging.warning('no title found for etext %s', etext)
        metadata[etext]['author'] = author
        metadata[etext]['title'] = title
    return dict(metadata)


def parse_etextno(xml):
    """Parses an etext meta-data definition to extract the etext-id field.

    Args:
        xml (xml.etree.ElementTree.Element): an etext meta-data definition

    Returns:
        int: the unique id of the etext or None if no id was found

    """
    ebook = xml.find(r'{http://www.gutenberg.org/2009/pgterms/}ebook')
    if ebook is None:
        return None
    about = ebook.get(r'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
    return int(os.path.basename(about))


def parse_author(xml):
    """Parses an etext meta-data definition to extract the author field.

    Args:
        xml (xml.etree.ElementTree.Element): an etext meta-data definition

    Returns:
        str: the author of the etext or None if no author was found

    """
    ebook = xml.find(r'{http://www.gutenberg.org/2009/pgterms/}ebook')
    creator = ebook.find(r'.//{http://purl.org/dc/terms/}creator')
    if creator is None:
        return None
    name = creator.find(r'.//{http://www.gutenberg.org/2009/pgterms/}name')
    return name.text if name is not None else None


def parse_title(xml):
    """Parses an etext meta-data definition to extract the title field.

    Args:
        xml (xml.etree.ElementTree.Element): an etext meta-data definition

    Returns:
        str: the title of the etext or None if no title was found

    """
    ebook = xml.find(r'{http://www.gutenberg.org/2009/pgterms/}ebook')
    title = ebook.find(r'.//{http://purl.org/dc/terms/}title')
    return title.text if title is not None else None


def raw_metainfo():
    """Retrieves an XML version of the Project Gutenberg meta-data catalog.

    Yields:
        xml.etree.ElementTree.Element: an etext meta-data definition

    """
    INDEX_URL = r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'
    filename, _ = urllib.urlretrieve(INDEX_URL)
    archive = tarfile.open(filename)
    for tarinfo in archive:
        yield ElementTree.XML('\n'.join(archive.extractfile(tarinfo)))


if __name__ == '__main__':
    import argparse

    doc = 'Downloads Project Gutenberg meta-data for all etexts as JSON'
    parser = argparse.ArgumentParser(description=doc)
    args = parser.parse_args()

    print json.dumps(metainfo(), sort_keys=True, indent=2)
