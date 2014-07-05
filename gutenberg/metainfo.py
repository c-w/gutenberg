"""Module to tag Project Gutenberg etexts with meta-data."""


from __future__ import absolute_import
import collections
import gutenberg.common.functutil as functutil
import gutenberg.common.stringutil as stringutil
import itertools
import json
import re
import requests


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
    return parse_index(raw_metainfo())


def raw_metainfo():
    """Retrieves the raw Project Gutenberg index via HTTP.

    Returns:
        list: the non-empty lines in the Project Gutenberg index

    """
    index = 'http://www.gutenberg.org/dirs/GUTINDEX.ALL'
    response = requests.get(index)
    rawtext = response.text
    return (line.strip() for line in rawtext.split('\n') if line)


def parse_index(lines):
    """Parses the Project Gutenberg index. Retrives information about works
    such as:
        - required: 'title', 'author'
        - optional: 'language', 'subtitle', 'editor', ...

    Args:
        lines (iter): the lines in the raw Project Gutenberg index

    Returns:
        dict: a mapping of etext number to meta information about the text

    Examples:
        >>> parse_index([
        ...     'Mystery Girl, by Wells      1',
        ...     '',
        ...     'Colonel Blood, by Abbott    2',
        ...     '[Language:en]',
        ...     '',
        ...     'Sky Detectives, by Newcomb  3',
        ...     '[Subtitle: How Jack',
        ...     'got his man]',
        ...     '[Language:en]',
        ... ]) == \
            {
        ...     1: {
        ...         'author': 'Wells',
        ...         'title': 'Mystery Girl',
        ...     },
        ...     2: {
        ...         'author': 'Abbott',
        ...         'language': 'en',
        ...         'title': 'Colonel Blood',
        ...     },
        ...     3: {
        ...         'author': 'Newcomb',
        ...         'language': 'en',
        ...         'subtitle': 'How Jack got his man',
        ...         'title': 'Sky Detectives',
        ...     },
        ... }
        True

        >>> parse_index([
        ...     'Very long title,             4',
        ...     ' by some author',
        ... ])
        {4: {'author': 'some author', 'title': 'Very long title'}}

    """
    lines = iter(lines)
    metadata = collections.defaultdict(dict)
    while True:
        try:
            (title, author, etext), lines = parse_entity(lines)
        except StopIteration:
            break

        metadata[etext]['title'] = title
        metadata[etext]['author'] = author
        extrainfo, lines = parse_extrainfo(lines)
        for key, value in extrainfo:
            metadata[etext][key.lower()] = value

    return dict(metadata)


def parse_entity(gutindex):
    """Parses the next (title, author, etext) tuple from the Project Gutenberg
    index. Note that this tuple may be split over one or two lines.

    Args:
        gutindex (iter): the lines in the raw Project Gutenberg index

    Returns:
        dict, iter: the next (title, author, etext) tuple in the index and an
                    iterator over the lines remaining to be parsed

    Examples:
        >>> lines = iter([
        ...     'Wood engraving, by R. Beedham       11',
        ...     'Life of Wm., by W. Fletcher Johnson 12',
        ...     '',
        ...     'Histoire de la monarchie,           13',
        ...     ' by Paul Thureau-Dangin',
        ...     'Oxford [City], by Andrew Lang[AL #25][oxfrdxxx.xxx] 2444',
        ...     'History, V2 by MacCaffrey [2hcthxxx.xxx] 2455',
        ...     'This line will not be consumed.',
        ... ])

        >>> entity, lines = parse_entity(lines)
        >>> entity
        ('Wood engraving', 'R. Beedham', 11)

        >>> entity, lines = parse_entity(lines)
        >>> entity
        ('Life of Wm.', 'W. Fletcher Johnson', 12)

        >>> entity, lines = parse_entity(lines)
        >>> entity
        ('Histoire de la monarchie', 'Paul Thureau-Dangin', 13)

        >>> entity, lines = parse_entity(lines)
        >>> entity
        ('Oxford', 'Andrew Lang', 2444)

        >>> entity, lines = parse_entity(lines)
        >>> entity
        ('History', 'MacCaffrey', 2455)

        >>> next(lines)
        'This line will not be consumed.'

    """
    lines = iter(gutindex)
    while True:
        line = next(lines)
        if not (line and line[-1].isdigit()):
            continue

        fullmatch = re.match(
            r'(?P<title>.+),.* by (?P<author>.+) (?P<etext>\d+)$', line)
        if fullmatch:
            title = fullmatch.group('title')
            author = fullmatch.group('author')
            etext = fullmatch.group('etext')
            break

        titlematch = re.match(r'(?P<title>.+), +(?P<etext>\d+)', line)
        authormatch = re.match(r' *by (?P<author>.*)', next(lines))
        if titlematch and authormatch:
            title = titlematch.group('title')
            etext = titlematch.group('etext')
            author = authormatch.group('author')
            break

    title = re.sub(r'\[[^]]*\]', '', title)
    author = re.sub(r'\[[^]]*\]', '', author)
    return (title.strip(), author.strip(), int(etext)), lines


def parse_extrainfo(gutindex):
    """Parses all the additional information for the current entity.

    Args:
        gutindex (iter): the lines in the raw Project Gutenberg index

    Returns:
        list, iter: (key, value) pairs providing meta-information about the
                    entity and the lines remaining to be parsed

    Examples:
        >>> lines = iter([
        ...     '[Subtitle: A study',
        ...     'of the ',
        ...     'ideals]',
        ...     '[Editor: Thomas Capek]',
        ...     '',
        ...     '[Author AKA: Francois Marie Arouet]',
        ...     'This line will not be consumed.',
        ...     '[Subtitle: From the Date]',
        ...     '[Author: William',
        ...     'Alexander',
        ...     'Linn]',
        ...     'This line will not be consumed.',
        ... ])

        >>> entities, lines = parse_extrainfo(lines)
        >>> entities
        [('Subtitle', 'A study of the ideals'), ('Editor', 'Thomas Capek')]

        >>> entities, lines = parse_extrainfo(lines)
        >>> entities
        [('Author AKA', 'Francois Marie Arouet')]

        >>> next(lines)
        'This line will not be consumed.'

        >>> entities, lines = parse_extrainfo(lines)
        >>> entities
        [('Subtitle', 'From the Date'), ('Author', 'William Alexander Linn')]

        >>> next(lines)
        'This line will not be consumed.'

    """
    lines, peek = itertools.tee(iter(gutindex), 2)
    key = value = None
    entities = []
    extrainfo_end = False

    while True:
        try:
            lookahead = next(peek)
        except StopIteration:
            break
        if extrainfo_end and lookahead and not lookahead.startswith('['):
            break
        try:
            line = next(lines)
        except StopIteration:
            break
        else:
            if not line:
                break

        if line.startswith('[') and line.endswith(']'):
            key, value = stringutil.splithead(line[1:-1], sep=':')
            entities.append((key, value.strip()))
            key = value = None
            extrainfo_end = True

        elif line.startswith('['):
            key, value = stringutil.splithead(line[1:], sep=':')
            extrainfo_end = False

        elif line.endswith(']') and key is not None:
            value = stringutil.merge(value, line[:-1])
            entities.append((key, value.strip()))
            key = value = None
            extrainfo_end = True

        else:
            value = stringutil.merge(value, line)

    return entities, lines


if __name__ == '__main__':
    import argparse

    doc = 'Downloads Project Gutenberg meta-data for all etexts as JSON'
    parser = argparse.ArgumentParser(description=doc)
    args = parser.parse_args()

    print json.dumps(metainfo(), sort_keys=True, indent=2)
