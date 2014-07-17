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
        int: the id of the etext

    Raises:
        ValueError: if no etext id was found

    Examples:
        >>> etextno(['Release Date: March 17, 2004 [EBook #11609]'])
        11609

        >>> etextno(['Release Date: July, 2003 [Etext# 4263]'])
        4263

        >>> etextno(['Release Date: November 29, 2003 [Eook #10335]'])
        10335

        >>> etextno(['December, 1998  [Etext 1576#]'])
        1576

        >>> etextno(['Some lines', 'without', 'Any [Etext] Number'])
        Traceback (most recent call last):
            ...
        ValueError: no etext-id found

    """

    etext_re = re.compile(r'''
        e(text|b?ook)
        \s*
        (\#\s*(?P<etextid_front>\d+)
         |
        (?P<etextid_back>\d+)\s*\#)
        ''', re.IGNORECASE | re.VERBOSE)
    for line in lines:
        match = etext_re.search(line)
        if match is not None:
            front_match = match.group('etextid_front')
            back_match = match.group('etextid_back')
            if front_match is not None:
                return int(front_match)
            elif back_match is not None:
                return int(back_match)
            else:
                raise ValueError('no regex match (this should never happen')
    raise ValueError('no etext-id found')


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
            logging.warning('no author meta-data found for etext %s', etext)
        if title is None:
            logging.warning('no title meta-data found for etext %s', etext)
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
    index_url = r'http://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'
    filename, _ = urllib.urlretrieve(index_url)
    with tarfile.open(filename) as archive:
        for tarinfo in archive:
            yield ElementTree.XML('\n'.join(archive.extractfile(tarinfo)))


def _main():
    """This function implements the main/script/command-line functionality of
    the module and will be called from the `if __name__ == '__main__':` block.

    """
    import gutenberg.common.cliutil as cliutil
    import argparse
    import sys

    doc = 'Downloads Project Gutenberg meta-data for all etexts as JSON'
    parser = cliutil.ArgumentParser(description=doc)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help=('the file to which to write the etext meta-data '
                              '(default: stdout)'))

    with parser.parse_args() as args:
        json.dump(metainfo(), args.outfile, sort_keys=True, indent=2)


if __name__ == '__main__':
    _main()
