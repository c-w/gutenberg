"""Module to deal with logging."""


from __future__ import absolute_import
import contextlib
import logging


@contextlib.contextmanager
def disable_logging(logger=None):
    """Context manager to temporarily suppress all logging for a given logger
    or the root logger if no particular logger is specified.

    """
    logger = logger or logging.getLogger()
    disabled = logger.disabled
    logger.disabled = True
    yield
    logger.disabled = disabled
