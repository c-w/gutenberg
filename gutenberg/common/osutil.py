"""Utility methods to deal with the file-system."""


import codecs
import errno
import itertools
import gzip
import os
import tempfile
import zipfile


def mkstemp(*args, **kwargs):
    """Returns the path of a new temporary file that can be opened for reading,
    writing, etc. The caller is responsible for deleting the temporary file.
    This function is a wrapper around tempfile.mkstemp that closes the returned
    file handle (without this, an OSError is thrown when trying to open the
    temporary path returned by tempfile.mkstemp on Windows).

    """
    handle, path = tempfile.mkstemp(*args, **kwargs)
    os.close(handle)
    return path


def stripext(path):
    """Removes the extension from a path.

    Args:
        path (str): the path from which to strip the extension

    Returns:
        str: the path without an extension

    Examples:
        >>> stripext('/foo/bar.ext')
        '/foo/bar'

        >>> stripext('/foo')
        '/foo'

        >>> stripext('foo.ext')
        'foo'

        >>> stripext('/')
        '/'

        >>> stripext('.')
        '.'

        >>> stripext('..')
        '..'

        >>> stripext('')
        ''

    """
    return os.path.splitext(path)[0]


def canonical(path):
    """Normalize a path.

    Args:
        path (str): the path to normalize

    Returns:
        str: an absolute version of the path with all variables expanded

    Examples:
        >>> import os

        >>> os.environ['BAZ'] = 'baz'
        >>> canonical('/foo/bar/$BAZ')
        '/foo/bar/baz'

        >>> os.chdir('/tmp')
        >>> canonical('foo/bar/../baz')
        '/tmp/foo/baz'

        >>> home = os.environ['HOME']
        >>> canonical('~/foo') == os.path.join(home, 'foo')
        True

    """
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path


def opener(path, mode='r', encoding=None):
    """Uses the appropriate open-method to open a file. Determines which
    open-method to use by looking at the extension of the file.

    Args:
        path (str): the path of the file to open
        mode (str, optional): the mode in which to open the file
        encoding (str, optional): the encoding with which to open the file

    Returns:
        file: the opened file

    """
    if path.endswith('.gz'):
        openfn = gzip.open
    else:
        openfn = open
    fileobj = openfn(path, mode)

    if encoding is not None:
        encoder = codecs.getreader if 'r' in mode else codecs.getwriter
        fileobj = encoder(encoding)(fileobj)

    return fileobj


def readfile(path, encoding=None):
    """Opens a file for reading. This is a wrapper around various file-opening
    methods that automatically determines which opener to use depending on the
    file's magic number.

    Args:
        path (str): the path of the file to open
        encoding (str, optional): the encoding with which to read the file

    Returns:
        iter: an iterator over the lines in the file

    Raises:
        NotImplementedError: if the file has a magic number for which no
                             opener has been implemented

    """
    path = canonical(path)
    magic = magic_number(path)
    lines = None

    if magic.startswith(magic_number.ZIP):
        zipf = zipfile.ZipFile(path)
        lines = itertools.chain(*[zipf.open(f) for f in zipf.namelist()])

    if magic.startswith(magic_number.GZIP):
        gzipf = gzip.open(path)
        lines = iter(gzipf)

    if lines is None:
        raise NotImplementedError(
            'Unsupported file with extension {ext} and magic number {magic}'
            .format(ext=os.path.splitext(path)[1], magic=magic))

    if encoding is not None:
        encoder = lambda line: unicode(line, encoding)
        lines = itertools.imap(encoder, lines)

    return lines


def magic_number(path):
    """Retrieves the magic number of a file.

    Args:
        path (str): the path from which to retrieve the magic number

    Returns:
        str: an upper-case hex-string representation of the magic number

    """
    with open(path, 'rb') as binary_file:
        magic = str(binary_file.read(4).encode('hex')).upper()
    return magic
magic_number.GZIP = '1F8B08'
magic_number.ZIP = '504B'


def listfiles(root, absolute=True):
    """Lists all the files in a directory and all of its subdirectories.

    Args:
        root (str): the top-level directory from which to list files
        absolute (bool, optional): output paths as absolute instead of relative

    Returns:
        iter: an iterator over the paths to all files under the top-level
              directory

    """
    finalize_path = canonical if absolute else lambda path: path
    root = finalize_path(root)
    for dirpath, subdirs, filenames in os.walk(root):
        for filename in filenames:
            yield finalize_path(os.path.join(dirpath, filename))
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
    path = canonical(path)
    try:
        os.makedirs(path)
    except (IOError, OSError) as ex:
        if ex.errno != errno.EEXIST:
            raise
