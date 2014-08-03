"""Utility methods to deal with strings."""


import re
import urlparse


def safeunicode(text, *args, **kwargs):
    """Converts a text to unicode. Unlike the builtin unicode conversion
    method, this function does not fail on text that already is unicode but
    simply returns the passed-in unicode text instead.

    Args:
        text (str): The text to convert to unicode.

    Returns:
        unicode: The text as unicode.

    Examples:
        >>> safeunicode('foo', 'utf-8')
        u'foo'

        >>> safeunicode(u'foo')
        u'foo'

    """
    if isinstance(text, unicode):
        return text

    return unicode(text, *args, **kwargs)


def request_param(param, url):
    """Extracts the value of a single http request parameter.

    Args:
        param (str): The request parameter whose value to extract.
        url (str): The request string from which to extract the paramter value.

    Returns:
        str: The value of the parameter or None if the paramter is not
            in the url.

    Examples:
        >>> request_param('baz', 'http://www.foo.com/bar?baz=1')
        '1'
        >>> request_param('grob', 'http://www.foo.com/bar?grob=2&baz=1')
        '2'
        >>> request_param('notfound', 'http://www.foo.com/bar?baz=1') is None
        True

    """
    query = urlparse.urlparse(url).query
    match = re.search('%s=([^&]*)&?' % param, query)
    return match.group(1) if match is not None else None


def merge(head, tail, sep=' '):
    """Null-safe and whitespace-consistent concatenation of two strings using a
    separator.

    Args:
        head (str): The string to concatenate left.
        tail (str): The string to concatenate right.
        sep (str, optional): The separator to use for concatenation.

    Returns:
        str: The string `head` + `sep` + `tail`.

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
        delimited (str): The string to split.
        sep (str, optional): The separator to split on.

    Returns:
        tuple: The first element split and the rest of the string.

    Examples:
        >>> splithead('foo bar')
        ('foo', 'bar')

        >>> splithead('foo:bar:baz', sep=':')
        ('foo', 'bar:baz')

    """
    tokens = delimited.split(sep)
    return tokens[0], sep.join(tokens[1:])
