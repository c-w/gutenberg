"""Utility methods to deal with the operating-system."""


import errno
import os


def makedirs(path):
    """Recrusively create all directories on a path.

    This is a wrapper around os.makedirs that doesn't fail if the directories
    already exist.

    Args:
        path (str): The path of directories to create

    Returns:
        str: The path of the created directories

    """
    try:
        os.makedirs(path)
    except (IOError, OSError) as ex:
        if ex.errno != errno.EEXIST:
            raise
    return path
