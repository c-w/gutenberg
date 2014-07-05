"""Utility methods to deal with the file-system."""


import errno
import itertools
import gzip
import os
import zipfile


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


def readfile(path):
    """Opens a file. This is a wrapper around various file-opening methods that
    automatically determines which opener to use depending on the file's magic
    number.

    Args:
        path (str): the path of the file to open

    Returns:
        iter: an iterator over the lines in the file

    """
    path = canonical(path)
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
    root = canonical(root)
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
    path = canonical(path)
    try:
        os.makedirs(path)
    except (IOError, OSError) as ex:
        if ex.errno != errno.EEXIST:
            raise
