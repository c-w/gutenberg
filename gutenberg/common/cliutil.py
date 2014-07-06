"""Utility methods to deal with command-line interfaces."""


import argparse
import logging


LOG_FORMAT = r'%(levelname)s:%(asctime)s:%(message)s'


class ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser subclass that has a default logging/verbosity argument
    and sets the loglevel accordingly. The parser also customizes the
    log-record format string.

    """
    def __init__(self, *args, **kwargs):
        self.logformat = kwargs.pop('logformat', LOG_FORMAT)
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.add_argument('-v', '--verbose', action='count',
                          help='increase logging verbosity')

    def parse_args(self, *args, **kwargs):
        argv = argparse.ArgumentParser.parse_args(self, *args, **kwargs)
        logging.basicConfig(
            level=loglevel(argv.verbose),
            format=self.logformat,
        )
        return argv


def loglevel(logval):
    """Converts an integer into the appropriate logging level. Higher values
    lead to more detailed logging, lower values lead to less detailed logging.

    Args:
        logval (int): the integer value to convert into a logging level

    Returns:
        int: the logging level corresponding to the integer value

    Examples:
        >>> loglevel(-2) == logging.CRITICAL
        True

        >>> loglevel(-1) == logging.ERROR
        True

        >>> loglevel(0) == logging.WARNING
        True

        >>> loglevel(1) == logging.INFO
        True

        >>> loglevel(2) == logging.DEBUG
        True

        >>> loglevel(3) == logging.NOTSET
        True

        >>> loglevel(123) == logging.NOTSET
        True

        >>> loglevel(-123) == logging.CRITICAL
        True

    """
    stdlvl, maxlvl, minlvl = logging.WARNING, logging.CRITICAL, logging.NOTSET
    return min(maxlvl, max(minlvl, stdlvl - 10 * logval))
