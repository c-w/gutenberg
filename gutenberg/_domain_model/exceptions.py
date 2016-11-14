"""Module to hold Gutenberg exceptions."""

from __future__ import unicode_literals


class Error(Exception):
    """Top level exception for the gutenberg library. All exceptions inherit
    from this class."""
    pass


class InvalidEtextIdException(Error):
    pass


class UnknownDownloadUriException(Error):
    pass


class UnsupportedFeatureException(Error):
    pass


class CacheAlreadyExistsException(Error):
    pass


class InvalidCacheException(Error):
    pass
