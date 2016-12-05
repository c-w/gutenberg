"""Module extending the functionality of the abc standard library module."""
# pylint: disable=C0103
# pylint: disable=R0903
# pylint: disable=W0622

from __future__ import unicode_literals


# noinspection PyPep8Naming
class abstractclassmethod(classmethod):
    """Decorator to indicate that a class-method needs to be over-written by
    all concrete implementations of a class.

    """
    __isabstractmethod__ = True

    def __init__(self, class_method):
        class_method.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(class_method)
