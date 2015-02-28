"""Module to deal with storing data files on disk."""


from __future__ import absolute_import
import os


def _root():
    """Returns the directory at which all other persisted files are rooted.

    """
    default_root = os.path.expanduser('~/gutenberg_data')
    return os.environ.get('GUTENBERG_DATA', default_root)


def local_path(path):
    """Returns a path that the caller may use to store local files.

    """
    return os.path.join(_root(), path)
