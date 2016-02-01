"""Module to hold Gutenberg exceptions."""


class Error(Exception):
    """Top level exception for the gutenberg library. All exceptions inherit
    from this class."""
    pass


class InvalidEtextId(Error):
    pass


class UnknownDownloadUri(Error):
    pass


class UnsupportedFeature(Error):
    pass


class CacheAlreadyExists(Error):
    pass


class CacheNotRemovable(Error):
    pass


class InvalidCache(Error):
    pass
