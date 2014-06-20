import collections
import json
import re
import requests


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
    metainfo = collections.defaultdict(dict)
    while True:
        try:
            title, author, etext = parse_entity(lines)
        except StopIteration:
            break

        metainfo[etext]['title'] = title
        metainfo[etext]['author'] = author
        for key, value in parse_extrainfo(lines):
            metainfo[etext][key.lower()] = value

    return dict(metainfo)


def parse_entity(lines):
    """Parses the next (title, author, etext) tuple from the Project Gutenberg
    index. Note that this tuple may be split over one or two lines.

    Args:
        lines (iter): the lines in the raw Project Gutenberg index

    Returns:
        dict: the next (title, author, etext) tuple in the index

    Examples:
        >>> lines = iter([
        ...     'Wood engraving, by R. Beedham       11',
        ...     'Life of Wm., by W. Fletcher Johnson 12',
        ...     '',
        ...     'Histoire de la monarchie,           13',
        ...     ' by Paul Thureau-Dangin',
        ...     'This line will not be consumed.',
        ... ])

        >>> parse_entity(lines)
        ('Wood engraving', 'R. Beedham', 11)

        >>> parse_entity(lines)
        ('Life of Wm.', 'W. Fletcher Johnson', 12)

        >>> parse_entity(lines)
        ('Histoire de la monarchie', 'Paul Thureau-Dangin', 13)

        >>> next(lines)
        'This line will not be consumed.'

    """
    lines = iter(lines)
    while True:
        line = next(lines)
        if not (line and line[-1].isdigit()):
            continue

        fullmatch = re.match(r'(.+), by (.+) (\d+)', line)
        if fullmatch:
            title, author, etext = fullmatch.groups()
            break

        titlematch = re.match(r'(.+), +(\d+)', line)
        authormatch = re.match(r' *by (.*)', next(lines))
        if titlematch and authormatch:
            title, etext = titlematch.groups()
            author = authormatch.group(1)
            break

    return title.strip(), author.strip(), int(etext)


def parse_extrainfo(lines):
    """Parses all the additional information for the current entity.

    Args:
        lines (iter): the lines in the raw Project Gutenberg index

    Returns:
        list: (key, value) pairs providing meta-information about the entity

    Examples:
        >>> list(parse_extrainfo([
        ...     '[Subtitle: A study',
        ...     'of the ',
        ...     'ideals]',
        ...     '[Editor: Thomas Capek]',
        ... ]))
        [('Subtitle', 'A study of the ideals'), ('Editor', 'Thomas Capek')]

    """
    lines = iter(lines)
    key = value = None
    while True:
        try:
            line = next(lines)
        except StopIteration:
            break
        else:
            if not line:
                break

        if line.startswith('[') and line.endswith(']'):
            key, value = splithead(line[1:-1], sep=':')
            yield key, value.strip()
            key = value = None

        elif line.startswith('['):
            key, value = splithead(line[1:], sep=':')

        elif line.endswith(']') and key is not None:
            value = merge(value, line[:-1])
            yield key, value.strip()
            key = value = None

        else:
            value = merge(value, line)


def merge(head, tail, sep=' '):
    """Null-safe and whitespace-consistent concatenation of two strings using a
    separator.

    Args:
        head (str): the string to concatenate left
        tail (str): the string to concatenate right
        sep (str, optional): the separator to use for concatenation

    Returns:
        str: the string "head + sep + tail"

    Examples:
        >>> merge('foo', 'bar')
        'foo bar'

        >> merge('foo ', 'bar')
        'foo bar'

        >>> merge('foo', '   bar')
        'foo bar'

        >>> merge(None, ' foo')
        'foo'

        >>> merge(' foo ', None)
        'foo'

        >>> merge(None, None)
        ''

    """
    return ((head or '').strip(sep) + sep + (tail or '').strip(sep)).strip(sep)


def splithead(delimited, sep=' '):
    """Splits off the first element in a delimited string.

    Args:
        delimited (str): the string to split
        sep (str, optional): the separator to split on

    Returns:
        tuple: the first element split and the rest of the string

    Examples:
        >>> splithead('foo bar')
        ('foo', 'bar')

        >>> splithead('foo:bar:baz', sep=':')
        ('foo', 'bar:baz')

    """
    tokens = delimited.split(sep)
    return tokens[0], sep.join(tokens[1:])


if __name__ == '__main__':
    import argparse

    doc = 'Downloads Project Gutenberg meta-data for all etexts as JSON'
    parser = argparse.ArgumentParser(description=doc)
    args = parser.parse_args()

    info = parse_index(raw_metainfo())
    print json.dumps(info, sort_keys=True, indent=2, separators=(',', ':'))
