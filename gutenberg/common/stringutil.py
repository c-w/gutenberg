import re
import urlparse


def request_param(param, url):
    """Extracts the value of a single http request parameter.

    Args:
        param (str): the request parameter whose value to extract
        url (str): the request string from which to extract the paramter value

    Returns:
        str: the value of the parameter or None if the paramter is not
             in the url

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
