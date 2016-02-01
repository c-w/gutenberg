"""Module to hold Gutenberg exceptions."""


class Error(Exception):
    """Top level exception for the gutenberg library. All other custom
    exceptions inherit from this class."""
    pass


class CacheAlreadyExists(Error):
    pass


class CacheNotRemovable(Error):
    pass


class InvalidCache(Error):
    pass
