"""Utility methods that deal with functions."""


import functools
import logging
import signal


def nointerrupt(fun):
    """Wrapper to ensure that a function always terminates. The current
    implementation relies on catching and discarding the SIGINT signal and
    therefore will only work on UNIX systems. Alternative implementations for
    Windows could implement a similar function using threads.

    Args:
        fun (function): The function to make un-interruptable.

    Returns:
        function: The un-interruptable version of the function.

    """

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Decorator."""
        sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
        retval = fun(*args, **kwargs)
        signal.signal(signal.SIGINT, sigint)
        return retval

    return wrapper


def ignore(*exceptions):
    """Decorator that evaluates a function and logs exceptions instead of
    throwing errors on them.

    Args:
        exceptions (list): The exceptions to ignore.

    Returns:
        function: The function with exception ignoring enabled.

    Examples:
        >>> d = {1: '1', 2: '2'}
        >>> @ignore(KeyError)
        ... def getter(dictionary, key):
        ...     return dictionary[key]
        >>> str(getter(d, 1))
        '1'

        >>> d_get = ignore(KeyError)(d.__getitem__)
        >>> str(d_get(2))
        '2'

        >>> str(getter(d, 'key not in dictionary'))
        'None'

        >>> str(d_get('key not in dictionary'))
        'None'

    """
    def decorator(fun):
        """Decorator with arguments."""
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            """Decorator."""
            try:
                retval = fun(*args, **kwargs)
            except Exception as ex:  # pylint: disable=W0703
                if not isinstance(ex, exceptions):
                    raise
                logging.error('ignored [%s] %s', type(ex).__name__, ex.message)
                retval = None
            return retval
        return wrapper

    return decorator


def memoize(fun):
    """Decorator that memoizes function return values. The memoization is
    implemented in a very naive manner and therefore shouldn't be used in
    anything critical. Most notably, the memoization cache is not limited in
    size.

    Args:
        fun (function): The function to decorate.

    Returns:
        function: The function with memoization enabled.

    """
    cache = fun._cache = {}

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """Decorator."""
        key = (args, frozenset(sorted(kwargs.items())))
        try:
            value = cache[key]
        except KeyError:
            value = cache[key] = fun(*args, **kwargs)
        return value

    return wrapper
