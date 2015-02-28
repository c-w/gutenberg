"""Module to hold utility methods dealing with types and classes."""


def all_subclasses(cls):
    """Recursively returns all the subclasses of the provided class.

    """
    subclasses = cls.__subclasses__()
    descendants = (descendant for subclass in subclasses
                   for descendant in all_subclasses(subclass))
    return set(subclasses) | set(descendants)
