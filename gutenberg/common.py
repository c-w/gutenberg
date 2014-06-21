"""Module for shared/common/utility functions."""


import errno
import functools
import gzip
import itertools
import os
import re
import signal
import urlparse
import zipfile


def nointerrupt(fun):
    """Wrapper to ensure that a function always terminates. The current
    implementation relies on catching and discarding the SIGINT signal and
    therefore will only work on UNIX systems. Alternative implementations for
    Windows could implement a similar function using threads.

    Args:
        fun (callable): the function to make un-interruptable

    Returns:
        callable: the un-interruptable version of the function

    """

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Decorator."""
        sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
        retval = fun(*args, **kwargs)
        signal.signal(signal.SIGINT, sigint)
        return retval

    return wrapper


def memoize(fun):
    """Decorator that memoizes function return values. The memoization is
    implemented in a very naive manner and therefore shouldn't be used in
    anything critical. Most notably, the memoization cache is not limited in
    size.

    Args:
        fun (callable): the function to decorate

    Returns:
        callable: the function with memoization enabled

    """
    cache = fun._cache = {}

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Decorator."""
        key = str(args) + str(kwargs)
        try:
            value = cache[key]
        except KeyError:
            value = cache[key] = fun(*args, **kwargs)
        return value

    return wrapper


def readfile(path):
    """Opens a file. This is a wrapper around various file-opening methods that
    automatically determines which opener to use depending on the file's magic
    number.

    Args:
        path (str): the path of the file to open

    Returns:
        iter: an iterator over the lines in the file

    """
    with open(path, 'rb') as binary_file:
        magic = str(binary_file.read(4).encode('hex')).upper()

    if magic.startswith('504B0304'):
        zipf = zipfile.ZipFile(path)
        try:
            return itertools.chain(*[zipf.open(f) for f in zipf.namelist()])
        finally:
            zipf.close()

    if magic.startswith('1F8B08'):
        with gzip.open(path) as gzipf:
            return iter(gzipf)

    raise ValueError(
        'Unsupported file with extension {ext} and magic number {magic}'
        .format(ext=os.path.splitext(path)[1], magic=magic))


def listfiles(root):
    """Lists all the files in a directory and all of its subdirectories.

    Args:
        root (str): the top-level directory from which to list files

    Returns:
        iter: an iterator over the paths to all files under the top-level
              directory

    """
    for dirpath, subdirs, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)
        for subdir in subdirs:
            listfiles(subdir)


def makedirs(path):
    """Recrusively create all directories on a path.

    This is a wrapper around os.makedirs that doesn't fail if the directories
    already exist.

    Args:
        path (str): the path of directories to create

    Examples:
        >>> makedirs('/tmp/foo/bar')
        >>> os.path.isdir('/tmp/foo/bar')
        True
        >>> makedirs('/tmp/foo/bar')

    """
    try:
        os.makedirs(path)
    except (IOError, OSError) as ex:
        if ex.errno != errno.EEXIST:
            raise


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
