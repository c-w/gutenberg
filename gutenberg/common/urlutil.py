"""Utility methods to deal with downloads and urls ."""


import hashlib
import logging
import os
import sys
import tempfile
import urllib


def channel_reporthook(channel):
    """Creates a reporthook that logs progress to some writeable object.

    """
    def reporthook(block_count, block_size, total_bytes):
        """Closure."""
        progress_bytes = block_count * block_size
        percent_progress = float(progress_bytes) / total_bytes * 100
        channel.write('Fetched %d/%d bytes (% 3.1f%%)\r'
                      % (progress_bytes,
                         total_bytes,
                         min(100, percent_progress)))

    return reporthook


def noop_reporthook():
    """Creates a reporthook that doesn't do anything.

    """
    def reporthook(*_):
        """Closure."""
        pass

    return reporthook


def default_reporthook(loglevel=logging.DEBUG, channel=sys.stderr):
    """Creats a reporthook that respects the current verbosity level.

    """
    if logging.getLogger().getEffectiveLevel() > loglevel:
        return noop_reporthook()
    return channel_reporthook(channel)


def urlretrieve(url, filename=None, reporthook=None, data=None, cached=True):
    """Wrapper around urllib.urlretrieve that caches results in /tmp.

    """
    if not filename:
        cachedir = tempfile.gettempdir()
        filename = os.path.join(cachedir, hashlib.sha256(url).hexdigest())

    if cached and os.path.isfile(filename):
        return filename, None

    reporthook = reporthook or default_reporthook()
    return urllib.urlretrieve(url, filename, reporthook, data)
