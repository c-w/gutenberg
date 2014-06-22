"""Utility methods that deal with functions."""


import functools
import signal


def nointerrupt(fun):
    """Wrapper to ensure that a function always terminates. The current
    implementation relies on catching and discarding the SIGINT signal and
    therefore will only work on UNIX systems. Alternative implementations for
    Windows could implement a similar function using threads.

    Args:
        fun (callable): the function to make un-interruptable

    Returns:
        callable: the un-interruptable version of the function

    """

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Decorator."""
        sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
        retval = fun(*args, **kwargs)
        signal.signal(signal.SIGINT, sigint)
        return retval

    return wrapper


def memoize(fun):
    """Decorator that memoizes function return values. The memoization is
    implemented in a very naive manner and therefore shouldn't be used in
    anything critical. Most notably, the memoization cache is not limited in
    size.

    Args:
        fun (callable): the function to decorate

    Returns:
        callable: the function with memoization enabled

    """
    cache = fun._cache = {}

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Decorator."""
        key = str(args) + str(kwargs)
        try:
            value = cache[key]
        except KeyError:
            value = cache[key] = fun(*args, **kwargs)
        return value

    return wrapper
